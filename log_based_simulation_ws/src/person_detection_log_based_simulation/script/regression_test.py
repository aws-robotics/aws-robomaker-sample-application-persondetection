#!/usr/bin/env python

import sys
import argparse
import rospy
from std_msgs.msg import String
from robomaker_simulation_msgs.msg import Tag
from robomaker_simulation_msgs.srv import Cancel, AddTags, ListTags


IS_CANCELLED = False
DEFAULT_BAG_CLOCK_TIMEOUT_SECONDS = 300


def cancel_job():
    requestCancel = rospy.ServiceProxy('/robomaker/job/cancel', Cancel)
    response = requestCancel()
    if response.success:
        global IS_CANCELLED
        IS_CANCELLED = True
        rospy.loginfo("Successfully requested cancel job")
    else:
        rospy.logerr("Cancel request failed: %s", response.message)


def add_tags(tags):
    ''' See Tag key and value rules: https://docs.aws.amazon.com/robomaker/latest/dg/API_TagResource.html '''
    requestAddTags = rospy.ServiceProxy('/robomaker/job/add_tags', AddTags)
    response = requestAddTags(tags)
    if not response.success:
        rospy.logerr("AddTags request failed for tags (%s): %s", tags, response.message)


def has_recognized_people(recognized_result):
    '''Pass the test if "I see" occurs at least once'''
    global IS_CANCELLED
    if IS_CANCELLED:
        return

    rospy.loginfo("Test is checking for recognized people.")
    if not IS_CANCELLED and recognized_result.data.strip()[:5] == 'I see':
        rospy.loginfo("We have recognized faces, test passed and cancelling job")
        add_tags([Tag(key="status", value="pass")])
        cancel_job()


def timeout_test(timer):
    rospy.loginfo("Test timeout called")
    if not IS_CANCELLED:
        rospy.loginfo("Test timed out, cancelling job")
        add_tags([Tag(key="status", value="timeout cancelled job")])
        cancel_job()
    else:
        rospy.loginfo("Test timed out, job already cancelled")
        add_tags([Tag(key="status", value="timeout job already cancelled")])


def run(clock_timeout):
    global TOPIC 
    rospy.init_node('robomaker_person_detection_regression_test')
    rospy.loginfo("Running AWS RoboMaker person detection regression test, /clock timeout is %s", clock_timeout)
    rospy.on_shutdown(on_shutdown)

    # The timeout ensures the /robomaker services are running before continuing. 
    rospy.wait_for_service('/robomaker/job/cancel', timeout=clock_timeout)
    rospy.wait_for_service('/robomaker/job/add_tags', timeout=clock_timeout)
    rospy.wait_for_service('/robomaker/job/list_tags', timeout=clock_timeout)

    # Tag this job as a test
    add_tags([Tag(key="robomaker_person_detection", value="regression_test")])

    # Now subscribe so we can check that we recognize a person
    rospy.Subscriber('/rekognized_people', String, has_recognized_people)

    # If the /clock takes too long, then timeout the test
    # Note: this will not timeout if the bags are not played back. For a wallclock 
    #       timeout, use the Job duration. 
    rospy.Timer(rospy.Duration(clock_timeout), timeout_test, oneshot=True)
    rospy.spin()


def on_shutdown():
    rospy.loginfo("Shutting down AWS RoboMaker person detection regression test node")


if __name__ == "__main__":
    global DEFAULT_BAG_CLOCK_TIMEOUT_SECONDS
    parser = argparse.ArgumentParser()
    parser.add_argument('--clock-timeout', type=int, default=DEFAULT_BAG_CLOCK_TIMEOUT_SECONDS, help='/clock topic timeout in seconds to cancel job')
    args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])
    run(clock_timeout=args.clock_timeout)
