import sys
import json

import six

from flux.wrapper import Wrapper, WrapperPimpl
from flux.core.inner import ffi, lib, raw
import flux.constants


class RPC(WrapperPimpl):
    """An RPC state object"""
    class InnerWrapper(Wrapper):

        def __init__(self,
                     flux_handle,
                     topic,
                     payload=None,
                     nodeid=flux.constants.FLUX_NODEID_ANY,
                     flags=0):
            # hold a reference for destructor ordering
            self._handle = flux_handle
            dest = raw.flux_future_destroy
            super(RPC.InnerWrapper, self).__init__(
                ffi, lib,
                handle=None,
                match=ffi.typeof(lib.flux_rpc).result,
                prefixes=['flux_rpc_'],
                destructor=dest)
            if isinstance(flux_handle, Wrapper):
                flux_handle = flux_handle.handle


            if payload is None or payload == ffi.NULL:
                payload = ffi.NULL
            elif not isinstance(payload, six.string_types):
                payload = json.dumps(payload)
            elif isinstance(payload, six.text_type):
                payload = payload.encode('UTF-8')

            self.handle = raw.flux_rpc(
                flux_handle, topic, payload, nodeid, flags)

    def __init__(self,
                 flux_handle,
                 topic,
                 payload=None,
                 nodeid=flux.constants.FLUX_NODEID_ANY,
                 flags=0):
        super(RPC, self).__init__()
        self.pimpl = self.InnerWrapper(flux_handle,
                                       topic,
                                       payload,
                                       nodeid,
                                       flags)
        self.then_args = None
        self.then_cb = None



    def get_str(self):
        j_str = ffi.new('char *[1]')
        try:
            self.pimpl.get(j_str)
            return ffi.string(j_str[0])
        except EnvironmentError as error:
            exception_tuple = sys.exc_info()
            try:
                errmsg = raw.flux_future_error_string(self.handle)
            except EnvironmentError:
                six.reraise(*exception_tuple)
            if errmsg is None:
                six.reraise(*exception_tuple)
            raise EnvironmentError(error.errno, errmsg.decode('utf-8'))

    def get(self):
        return json.loads(self.get_str().decode('utf-8'))
