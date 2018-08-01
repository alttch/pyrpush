# pyrpush
Push client Python library for Roboger event pager (https://www.roboger.com/,
https://github.com/alttch/roboger)

License: Apache License 2.0

Usage example:
 
```python
from pyrpush import Client as RPushClient

r = RPushClient()
r.push(msg='test message')
r.push(msg='test2', media_file='1.jpg', level='warning')
```

(c) 2018 Altertech Group, https://www.altertech.com/

