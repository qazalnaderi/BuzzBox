from concurrent import futures
import grpc
from loguru import logger
from app.core.config.config import get_settings
from app.grpc_service import media_pb2_grpc, media_pb2
from app.infrastructure.clients.iam_client import IAMClient
from app.services.media_service import MediaService
from app.infrastructure.repositories.media_repository import MediaRepository
from app.infrastructure.storage.gridfs_storage import GridFsStorage
from app.core.db.mongo_db import db
import asyncio

config = get_settings()


class MediaServiceServicer(media_pb2_grpc.MediaServiceServicer):
    def __init__(self, media_service: MediaService, iam_client: IAMClient):
        self.media_service = media_service
        self.iam_client = iam_client

    async def DownloadMedia(self, request, context):
        # Extract the user filed from the metadata
        user_id = dict(context.invocation_metadata()).get("user")

        try:
            media_data = await self.media_service.get_media_data(request.media_id, user_id)
            if media_data is None:
                logger.error(f"Media not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Media not found")
                return media_pb2.MediaResponse()

            logger.info(f"Media {request.media_id} retrieved")
            return media_pb2.MediaResponse(
                media_data=media_data, media_type=request.media_type
            )
        except Exception as e:
            logger.error(f"Error retrieving media: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return media_pb2.MediaResponse()

import grpc.experimental.aio as aio
async def serve():
    try:
        logger.info("Starting gRPC server initialization...")
        
        logger.info("Loading configuration...")
        config = get_settings()
        logger.info(f"Configuration loaded: GRPC_PORT={config.GRPC_PORT}")
        
        logger.info("Creating gRPC server...")
        options = [
            ('grpc.max_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ('grpc.max_send_message_length', 100 * 1024 * 1024)
        ]
        server = aio.server(options=options)
        
        logger.info("Initializing database connection...")
        db_instance = db
        logger.info("Database connection established")
        
        logger.info("Initializing services...")
        media_repository = MediaRepository(db_instance)
        storage = GridFsStorage(db_instance)
        media_service = MediaService(media_repository, storage)
        iam_client = IAMClient(config)
        logger.info("Services initialized successfully")
        
        media_pb2_grpc.add_MediaServiceServicer_to_server(
            MediaServiceServicer(media_service, iam_client),
            server
        )
        
        addr = f"[::]:{config.GRPC_PORT}"
        logger.info(f"Binding to address: {addr}")
        port = server.add_insecure_port(addr)
        if port == 0:
            raise RuntimeError(f"Failed to bind to address {addr}")
        
        logger.info("Starting server...")
        await server.start()
        logger.info(f"Server started successfully on port {config.GRPC_PORT}")
        
        await server.wait_for_termination()
        
    except Exception as e:
        logger.error(f"Failed to start gRPC server: {str(e)}")
        logger.exception("Full traceback:")  # This will print the full stack trace
        raise


def main():
    try:
        logger.info("Initializing gRPC server main process")
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in gRPC server: {str(e)}")
        logger.exception("Full traceback:")
        exit(1)


if __name__ == "__main__":
    main()