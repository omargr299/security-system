import enum


class Modes(enum.Enum):
    Cient = "client"
    Detector = "detector"


class Service(enum.Enum):
    Face = "face"
    QR = "qr"
    Plates = "plates"

    def getValues():
        return [s.value for s in Service]


class MessageTypes(enum.Enum):
    Service = "service"
    Exit = "exit"
    Image = "image"
    Receiving = "receiving"
    Camera = "camera"
    Sending = "sending"
    Success = "success"
    Fail = "fail"
    Login = "login"


class LoginMessages(enum.Enum):
    username = "username"
    password = "password"
    success = "success"


if __name__ == "__main__":
    service = Service.Face.value
