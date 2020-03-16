__author__ = "Altertech Group, https://www.altertech.com/"
__copyright__ = "Copyright (C) 2018 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.1.3"

from configparser import ConfigParser
import requests
import base64
import time
import logging
import platform
import getpass

default_timeout = 5
default_ini_file = '/usr/local/etc/roboger_push.ini'


class RobogerClient(object):

    def __init__(self, ini_file=None):
        """
        Args:
            ini_file: config file to parse (equal to roboger_push cfg)

        Raises:
            Exception: if no config file or config file is empty/invalid
        """
        inif = ini_file if ini_file else default_ini_file
        cp = ConfigParser(inline_comment_prefixes=';')
        cp.read(inif)
        self.cdict = {s: dict(cp.items(s)) for s in cp.sections()}
        if not self.cdict:
            self._log_error('unable to parse config file: %s' % inif)
        self.sender = None
        self.location = None

    def push(self, msg='', media_file=None, **kwargs):
        """Push message via Roboger server(s)

        Args:
            addr: roboger address, if not specified, address from config file
                  will be use
            msg: message text, optional
            subject: message subject, optional
            sender: if not specified, sender from config file will be used
            location: event location, optional
            tag: event tag
            level: debug, info, warning, error or critical (you can use first
                   letter only)
            media: base64-encoded media, optional
            media_file: get media from file, string or file descriptor, optional

        Returns:
            bool: True if at least one server accepted push, False otherwise

        Raises:
            FileNotFoundError: if the specified media file is unavailable
        """
        data = kwargs.copy()
        data['msg'] = msg
        # TODO: remove legacy keywords
        if 'keywords' in data:
            if isinstance(data['keywords'], list):
                data['keywords'] = ','.join(data['keywords'])
            data['tag'] = data['keywords']
            del data['keywords']
        if media_file:
            if isinstance(media_file, str):
                f = open(media_file, 'rb')
            else:
                f = media_file
            data['media'] = base64.b64encode(f.read())
        try:
            # we need text, but b64-encoded media can be bytes
            data['media'] = data['media'].decode()
        except:
            pass
        sent = False
        for i, srv in self.cdict.items():
            if srv.get('type') != 'backup':
                if self._push_via(i, **data): sent = True
        return sent

    # internal methods

    def _push_via(self, srv_id, **kwargs):
        srv = self.cdict[srv_id]
        uri = srv.get('push')
        data = kwargs.copy()
        if not uri: return
        try:
            tries = int(srv.get('retries')) + 1
        except:
            tries = 1
        try:
            retry_delay = int(srv.get('retry_delay'))
        except:
            retry_delay = 1
        try:
            timeout = int(srv.get('timeout'))
        except:
            timeout = None
        if not 'sender' in data:
            if self.sender is not None:
                data['sender'] = self.sender
            elif 'sender' in srv:
                data['sender'] = srv['sender']
            else:
                data['sender'] = '%s@%s' % (getpass.getuser(), platform.node())
        if not 'location' in data:
            if self.location is not None:
                data['location'] = self.location
            elif 'location' in srv:
                data['location'] = srv['location']
            else:
                data['location'] = platform.node()
        if not 'addr' in data and 'addr' in srv:
            data['addr'] = srv['addr']
        sent = False
        for x in range(tries):
            if self._send_push(uri, timeout, **data):
                sent = True
                break
            time.sleep(retry_delay)
        if not sent:
            self._log_warning('failed to send rpush to %s' % uri)
            backup = srv.get('backup')
            if backup in self.cdict:
                return self._push_via(backup, **kwargs)
            return False
        return True

    def _send_push(self, uri, timeout=None, **kwargs):
        _timeout = timeout if timeout else default_timeout
        try:
            self._log_debug('sending push to %s' % uri)
            r = requests.post(uri + '/push', json=kwargs, timeout=_timeout)
            if r.status_code not in [200, 202]:
                raise Exception('rpush error, code %u' % r.status_code)
        except:
            self._log_debug('rpush to %s failed' % uri)
            return False
        self._log_debug('success rpush to %s' % uri)
        return True

    def _log_debug(self, msg):
        logging.debug('RobogerClient: %s' % msg)

    def _log_warning(self, msg):
        logging.warning('RobogerClient: %s' % msg)

    def _log_error(self, msg, raise_exception=True):
        logging.error('RobogerClient: %s' % msg)
        if raise_exception: raise Exception(msg)
