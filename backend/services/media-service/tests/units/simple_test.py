def test_bson_import():
    try:
        from bson import ObjectId
        print("Successfully imported ObjectId:", ObjectId)
    except ImportError as e:
        print("ImportError:", e)
        raise e
