import rospy
from std_msgs.msg import String

from stick import Stick


class StickManager:
    left_stick = None
    right_stick = None

    def __init__(self):
        rospy.init_node("sticks_controller")
        rospy.loginfo("Sticks node started")
        rospy.Subscriber("tempo", String, self.on_tempo)
        rospy.Subscriber("style", String, self.on_style)
        rospy.Subscriber("animation", String, self.on_animation)
        self.left_stick = Stick(True, 80, [0, 1])
        self.right_stick = Stick(False, 80, [2, 3])
        rospy.spin()

    # message of type: <start|duration>:rhythm:initial_tempo or stop
    # (e.g., start:four_four:80 or 3000:three_four:120 or stop)
    def on_animation(self, data):
        if data.data == "stop":
            self.left_stick.stop_animate()
            self.right_stick.stop_animate()
        else:
            animation = data.data.split(":")
            print(animation)
            if animation[0] == "start":
                self.left_stick.start_animate(
                    rhythm=animation[1], duration="indefinite", initial_tempo=animation[2])
                self.right_stick.start_animate(
                    rhythm=animation[1], duration="indefinite", initial_tempo=animation[2])
            else:
                self.left_stick.start_animate(
                    rhythm=animation[1], duration=animation[0], initial_tempo=animation[2])
                self.right_stick.start_animate(
                    rhythm=animation[1], duration=animation[0], initial_tempo=animation[2])

    # message of type: tempo (e.g., 80)
    def on_tempo(self, data):
        self.left_stick.set_new_tempo(data.data)
        self.right_stick.set_new_tempo(data.data)

    # message of type: style (e.g., four_four)
    def on_style(self, data):
        self.left_stick.set_rhythm(data.data)
        self.right_stick.set_rhythm(data.data)


if __name__ == "__main__":
    sm = StickManager()

