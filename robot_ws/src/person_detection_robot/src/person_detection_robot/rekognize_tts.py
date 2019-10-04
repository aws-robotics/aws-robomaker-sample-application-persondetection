#!/usr/bin/env python
"""
 Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

 Permission is hereby granted, free of charge, to any person obtaining a copy of this
 software and associated documentation files (the "Software"), to deal in the Software
 without restriction, including without limitation the rights to use, copy, modify,
 merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import time
import json

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.action import ActionClient

from tts_interfaces.srv import Synthesizer
from std_msgs.msg import String

class Rekognizer(Node):

    def __init__(self, rekognition_topic="/rekognition/results"):
        super().__init__('rekognize_tts')
        Gst.init(None)
        #Listen for rekognition results
        self.rekognition_subscriber = self.create_subscription(String, rekognition_topic, self.rekognize_callback, 10)
        #Action client for Polly
        self.synthesizer = self.create_client(Synthesizer, 'synthesizer')

    def handle_result(self, synthesizer_response):
        result = synthesizer_response.result
        try:
            r = json.loads(result)
        except Exception as e:
            s = 'Expecting JSON from synthesizer but got {}'.format(result)
            self.get_logger().error('{}. Exception: {}'.format(s, e))
            return

        result = ''

        if 'Audio File' in r:
            audio_file = r['Audio File']
            print(audio_file)
            self.get_logger().info('Will play {}'.format(audio_file))
            self.play(audio_file)
            result = audio_file

        if 'Exception' in r:
            result = '[ERROR] {}'.format(r)
            self.get_logger().error(result)

        return result

    def play(self, filename):
        self.get_logger().info('using gstreamer to play the audio')

        playbin = Gst.ElementFactory.make('playbin', 'player')

        bus = playbin.get_bus()

        playbin.props.uri = 'file://' + os.path.abspath(filename)
        time.sleep(0.5)  # sometimes gst needs time to get ready for unknown reasons
        set_result = playbin.set_state(Gst.State.PLAYING)
        if set_result != Gst.StateChangeReturn.ASYNC:
            raise RuntimeError("gstreamer error: playbin.set_state returned " + repr(set_result))

        bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
        playbin.set_state(Gst.State.NULL)

    def on_synthesize_done(self, future):
        if future.result():
            self.get_logger().info(f'Result: {str(future.result())}')
            self.handle_result(future.result())
            self.get_logger().info(f'Done speaking {self.req.text}')
        else:
            self.get_logger().error(f'Exception while calling service: {future.exception()}')

    def rekognize_callback(self, msg):
        image_ids = []
        try:
            msg = json.loads(msg.data)
            if msg["FaceSearchResponse"]:
                self.get_logger().debug("Rekognition result has FaceSeachResponse, looking for matched faces")
                for face in msg['FaceSearchResponse'][0]['MatchedFaces']:
                    self.get_logger().debug(f"Matched face: {face}")
                    # Default 'unnamed' is required for indexed images without ExternalImageId
                    name = face['Face'].get('ExternalImageId', 'unknown')
                    self.get_logger().debug(f"Matched face has name: {name}")
                    image_ids.append(name)
            else:
                return
        except ValueError as e:
            self.get_logger().error(f"Error loading json message from rekognition:\n{e}")
            return

        if not image_ids:
            self.get_logger().info('Rekognition result has no faces')
            return 

        names =" and ".join([image_id.replace("_"," ") for image_id in image_ids])

        #Create Polly Request
        self.req = Synthesizer.Request()
        self.req.text = "I see {}".format(names)

        while not self.synthesizer.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('service not available, waiting again...')

        future = self.synthesizer.call_async(self.req)
        future.add_done_callback(self.on_synthesize_done)

def main(args=None):
    rclpy.init(args=args)
    rotator = Rekognizer()
    rclpy.spin(rotator)

if __name__ == '__main__':
    main()
