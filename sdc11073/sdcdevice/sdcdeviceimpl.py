from .. import pmtypes
from .sdc_handlers import SdcHandler_Full


class SdcDevice(object):
    def __init__(self, my_uuid, ws_discovery, model, device, deviceMdibContainer, validate=True, roleProvider=None, useSSL=True, sslContext=None,
                 logLevel=None, max_subscription_duration=7200, log_prefix='', handler_cls=None): #pylint:disable=too-many-arguments
        # ssl protocol handling itself is delegated to a handler.
        # Specific protocol versions or behaviours are implemented there.
        if handler_cls is None:
            handler_cls = SdcHandler_Full
        self._handler = handler_cls(my_uuid, ws_discovery, model, device, deviceMdibContainer, validate,
                                roleProvider, useSSL, sslContext, logLevel, max_subscription_duration,
                                log_prefix=log_prefix)
        self._wsdiscovery = ws_discovery
        self._logger = self._handler._logger
        self._mdib = deviceMdibContainer


    @property
    def shallValidate(self):
        return self._handler._validate

    @property
    def mdib(self):
        return self._mdib

    @property
    def subscriptionsManager(self):
        return self._handler._subscriptionsManager

    @property
    def scoOperationsRegistry(self):
        return self._handler._scoOperationsRegistry

    @property
    def epr(self):
        # End Point Reference, e.g 'urn:uuid:8c26f673-fdbf-4380-b5ad-9e2454a65b6b'
        return self._handler._my_uuid.urn

    @property
    def path_prefix(self):
        # http path prefix of service e.g '8c26f673-fdbf-4380-b5ad-9e2454a65b6b'
        return self._handler.path_prefix

    def registerOperation(self, operation):
        return self._handler.registerOperation(operation)

    def unRegisterOperationByHandle(self, operationHandle):
        return self._handler.unRegisterOperationByHandle(operationHandle)

    def getOperationByHandle(self, operationHandle):
        return self._handler.getOperationByHandle(operationHandle)

    def enqueueOperation(self, operation, request):
        return self._handler.enqueueOperation(operation, request)

    def dispatchGetRequest(self, parseResult, headers):
        ''' device itself can also handle GET requests. This is the handler'''
        return self._handler.dispatchGetRequest(parseResult, headers)

    def startAll(self, startRealtimeSampleLoop=True, shared_http_server = None):
        """

        :param startRealtimeSampleLoop: flag
        :param shared_http_server: id provided, use this http server. Otherwise device creates its own.
        :return:
        """
        return self._handler.startAll(startRealtimeSampleLoop, shared_http_server)

    def stopAll(self, closeAllConnections=True, sendSubscriptionEnd=True):
        return self._handler.stopAll(closeAllConnections, sendSubscriptionEnd)

    def getXAddrs(self):
        return self._handler.getXAddrs()


    def sendMetricStateUpdates(self, mdibVersion, stateUpdates):
        return self._handler.sendMetricStateUpdates(mdibVersion, stateUpdates)

    def sendAlertStateUpdates(self, mdibVersion, stateUpdates):
        return self._handler.sendAlertStateUpdates(mdibVersion, stateUpdates)

    def sendComponentStateUpdates(self, mdibVersion, stateUpdates):
        return self._handler.sendComponentStateUpdates(mdibVersion, stateUpdates)

    def sendContextStateUpdates(self, mdibVersion, stateUpdates):
        return self._handler.sendContextStateUpdates(mdibVersion, stateUpdates)

    def sendOperationalStateUpdates(self, mdibVersion, stateUpdates):
        return self._handler.sendOperationalStateUpdates(mdibVersion, stateUpdates)

    def sendRealtimeSamplesStateUpdates (self, mdibVersion, stateUpdates):
        return self._handler.sendRealtimeSamplesStateUpdates(mdibVersion, stateUpdates)

    def sendDescriptorUpdates(self, mdibVersion, updated, created, deleted, updated_states):
        return self._handler.sendDescriptorUpdates(mdibVersion, updated, created, deleted, updated_states)

    def sendWaveformUpdates(self, changedSamples):
        return self._handler.sendWaveformUpdates(changedSamples)

    def setUsedCompression(self, *compression_methods):
        return self._handler.setUsedCompression(*compression_methods)

    @property
    def product_roles(self):
        return self._handler.product_roles

    @product_roles.setter
    def product_roles(self, product_roles):
        self._handler.product_roles = product_roles



class PublishingSdcDevice(SdcDevice):
    defaultInstanceIdentifiers = (pmtypes.InstanceIdentifier(root='rootWithNoMeaning', extensionString='System'),)

    def __init__(self, ws_discovery, my_uuid, model, device, deviceMdibContainer, validate=True,
                 roleProvider=None, useSSL=True, sslContext=None, logLevel=None,
                 max_subscription_duration=7200, log_prefix='', handler_cls=None):
        """
        @param ws_discovery: reference to the wsDiscovery instance
        @param uuid: a string that becomes part of the devices url (no spaces, no special characters please. This could cause an invalid url!).
                     Parameter can be None, in this case a random uuid string is generated.
        @param model: a pysoap.soapenvelope.DPWSThisModel instance
        @param device: a pysoap.soapenvelope.DPWSThisDevice instance
        @param deviceMdibContainer: a DeviceMdibContainer instance
        @param validate: activates schema validation
        @param roleProvider: if provided, ait defines the behaviour of the device ( reactions on operation calls)
        @param useSSL: determines if http or https is used
        @param sslContext: if not None, this context is used. Otherwise a sSSLContext is automatically generated.
        @param logLevel: if not None, the "sdc.device" logger will use this level
        @param max_subscription_duration: max. possible duration of a subscription, default is 7200 seconds
        @param ident: names a device, used for logging
        """
        super(PublishingSdcDevice, self).__init__(my_uuid, ws_discovery, model, device, deviceMdibContainer, validate,
                                                  roleProvider, useSSL, sslContext, logLevel,
                                                  max_subscription_duration=max_subscription_duration,
                                                  log_prefix=log_prefix, handler_cls=handler_cls)
        self._location = None

    def setLocation(self, location, validators=defaultInstanceIdentifiers, publishNow=True):
        '''
        @param location: a pysdc.location.DraegerLocation instance
        @param validators: a list of pmtypes.InstanceIdentifier objects or None; in that case the defaultInstanceIdentifiers member is used
        @param publishNow: if True, the device is published via its wsdiscovery reference.
        '''
        if location == self._location:
            return

        if self._location is not None:
            self._wsdiscovery.clearService(self.epr)

        self._location = location

        if location is None:
            return

        self._mdib.setLocation(location, validators)
        if publishNow:
            self.publish()

    def publish(self):
        """
        publish device on the network (sends HELLO message)
        :return:
        """
        scopes = self._handler.mkScopes()
        xAddrs = self.getXAddrs()
        self._wsdiscovery.publishService(self.epr, self._mdib.sdc_definitions.MedicalDeviceTypesFilter, scopes, xAddrs)

