class Spam:
    val = 100

    def ham(self):
        self.egg('call method')

    def egg(self, msg):
        print("{0}".format(msg))
        print(("{0}".format(self.val)))


def hello():
    print("hell0")


val = 10
