# pyrpush
Push client Python library for Roboger event pager (https://www.roboger.com/,
https://github.com/alttch/roboger)

License: Apache License 2.0

Usage example:
 
```python
from pyrpush import Client as RPushClient

r = RPushClient()
r.sender = 'bot1'
r.location = 'lab'
r.push(msg='test message')
r.push(msg='test2', media_file='1.jpg', level='warning')
```

Constructor can accept *ini_file=FILENAME* param as the alternative config
location.

(c) 2018-2019 Altertech Group, https://www.altertech.com/

