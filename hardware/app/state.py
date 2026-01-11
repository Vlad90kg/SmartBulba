class SystemState:
    def __init__(self):
        self.mode = "motion"      # motion | manual
        self.power = False
        self.brightness = "medium"

state = SystemState()

