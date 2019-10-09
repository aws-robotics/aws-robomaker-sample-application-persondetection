#!/usr/bin/env python3
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

import json

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

class Rekognizer(Node):

    def __init__(self, rekognition_topic="/rekognition/results"):
        super().__init__('rekognize')
        #Listen for rekognition results
        self.rekognition_subscriber = self.create_subscription(String,
                                                               rekognition_topic,
                                                               self.rekognize_callback,
                                                               10)
        #Publish names extraced from rekognition results
        self.output_publisher = self.create_publisher(String,
                                                      "/rekognized_people")

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

        names = " and ".join([image_id.replace("_", " ") for image_id in image_ids])
        text = String()
        text.data = "I see {}".format(names)
        self.output_publisher.publish(text)
        self.get_logger().info(text.data)

def main(args=None):
    rclpy.init(args=args)
    rekognizer = Rekognizer()
    rclpy.spin(rekognizer)
    rekognizer.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
