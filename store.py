from collections import OrderedDict
from datetime import datetime, timedelta
from threading import Lock


class MemoryStore:
    def __init__(self):
        self.obj = OrderedDict()
        self.lock = Lock()
        self.max_obj = 10

    def _is_expired(self, expired_at):
        if expired_at is None :
            return False
        elif expired_at <= datetime.now():
            return True
        else:
            return False
        
    def _remove_expired(self):
        keys_to_delete = []
        for key, (value, expired_at) in self.obj.items():
            if self._is_expired(expired_at):
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.obj[key]

    def put(self, key, value, ttl_seconds):
        with self.lock:
            expired_at = None
            self._remove_expired()
            if ttl_seconds > 0:
                expired_at = datetime.now() + timedelta(seconds=ttl_seconds)
            if key not in self.obj:
                self.obj[key] = (value, expired_at)
                if len(self.obj) > self.max_obj:
                    self.obj.popitem(last=False)
            else:
                self.obj[key] = (value, expired_at)
                self.obj.move_to_end(key)
            
    def get(self, key):
        with self.lock:
            self._remove_expired()
            if key in self.obj:
                self.obj.move_to_end(key)
                return self.obj[key][0]
            return None
                
    def delete(self, key):
        with self.lock:
            self._remove_expired()
            if key in self.obj:
                del self.obj[key]
                return True
            return False
    
    def list(self, prefix):
        with self.lock:
            self._remove_expired()
            res = []
            for key, (value, expired_at) in self.obj.items():
                if key.startswith(prefix):
                    res.append((key, value))
            return res    
        
        
    

