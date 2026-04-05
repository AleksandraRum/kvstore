import grpc
from concurrent import futures

import kvstore_pb2
import kvstore_pb2_grpc

from store import MemoryStore

class KeyValueStoreService(kvstore_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.store = MemoryStore()

    def Put(self, request, context):
        self.store.put(request.key, request.value, request.ttl_seconds)
        return kvstore_pb2.PutResponse()
    
    def Get(self, request, context):
        value = self.store.get(request.key)
        if value is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "key not found")
        return kvstore_pb2.GetResponse(value=value)
    
    def Delete(self, request, context):
        value = self.store.delete(request.key)
        if not value:
            context.abort(grpc.StatusCode.NOT_FOUND, "key not found")
        return kvstore_pb2.DeleteResponse()
    
    def List(self, request, context):
        items = self.store.list(request.prefix)
        res = []
        for key, value in items:
            res.append(
                kvstore_pb2.KeyValue(key=key, value=value)
            )

        return kvstore_pb2.ListResponse(items=res)
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kvstore_pb2_grpc.add_KeyValueStoreServicer_to_server(
    KeyValueStoreService(),
    server
    )
    server.add_insecure_port("[::]:8000")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()