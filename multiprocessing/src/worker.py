# Python Standard Library
import sys

# Third-Party Libraries
import cloudpickle as pickle

# Local Library
from core import mailbox

sender = sys.argv[1]
print(mailbox.id, flush=True)

message = next(mailbox)
(fct, args, kwargs) = pickle.loads(message["data"])
out = fct(*args, **kwargs)
mailbox.send(sender, mailbox.id.encode("utf-8") + pickle.dumps(out))
