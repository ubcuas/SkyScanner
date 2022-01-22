class scannerClient:
    def __init__(self):
        self._questionResponse = []
        self._dateResponse = "No date scanned"
        self._timeResponse = "No time scanned"
        self._deviceResponse = "No device scanned"
        self._sensorResponse = "No sensor scanned"
        self._coordLatResponse = "No coord scanned"
        self._coordLonResponse = "No coord scanned"

    @property
    def questionResponse(self):
        return self._questionResponse

    @questionResponse.setter
    def questionResponse(self, value):
        self._questionResponse = value

    @questionResponse.deleter
    def questionResponse(self):
        del self._questionResponse

    @property
    def dateResponse(self):
        return self._dateResponse

    @dateResponse.setter
    def dateResponse(self, value):
        self._dateResponse = value

    @dateResponse.deleter
    def dateResponse(self):
        del self._dateResponse
        
    @property
    def deviceResponse(self):
        return self._deviceResponse

    @deviceResponse.setter
    def deviceResponse(self, value):
        self._deviceResponse = value

    @deviceResponse.deleter
    def deviceResponse(self):
        del self._deviceResponse

    @property
    def sensorResponse(self):
        return self._sensorResponse

    @sensorResponse.setter
    def sensorResponse(self, value):
        self._sensorResponse = value

    @sensorResponse.deleter
    def sensorResponse(self):
        del self._sensorResponse

    @property
    def coordLatResponse(self):
        return self._coordLatResponse

    @coordLatResponse.setter
    def coordLatResponse(self, value):
        self._coordLatResponse = value

    @coordLatResponse.deleter
    def coordLatResponse(self):
        del self._coordLatResponse
        
    @property
    def coordLonResponse(self):
        return self._coordLonResponse

    @coordLonResponse.setter
    def coordLonResponse(self, value):
        self._coordLonResponse = value

    @coordLonResponse.deleter
    def coordLonResponse(self):
        del self._coordLonResponse