"""Supervisor of the Robot Programming benchmark."""

from controller import Supervisor
import os
import sys

# Constant used for the automated benchmark evaluation script
# - can also be used to generate an animation in storage folder if set to True
RECORD_ANIMATION = False

if RECORD_ANIMATION:
    import recorder.recorder as rec

def benchmarkPerformance(message, robot):
    benchmark_name = message.split(':')[1]
    benchmark_performance_string = message.split(':')[3]
    print(benchmark_name + ' Benchmark complete! Your performance was ' + benchmark_performance_string)

robot = Supervisor()

timestep = int(robot.getBasicTimeStep())

thymio = robot.getFromDef("BENCHMARK_ROBOT")
translation = thymio.getField("translation")

if RECORD_ANIMATION:
    # Recorder code: wait for the controller to connect and start the animation
    rec.animation_start_and_connection_wait(robot)
    step_max = 1000 * rec.MAX_DURATION / timestep
    step_counter = 0

tx = 0
running = True
while robot.step(timestep) != -1 and running:
    t = translation.getSFVec3f()
    if running:
        percent = 1 - abs(0.25 + t[0]) / 0.25
        if percent < 0:
            percent = 0
        if t[0] < -0.01 and abs(t[0] - tx) < 0.0001:  # away from starting position and not moving any more
            running = False
            name = 'Robot Programming'
            performance = str(percent)
            performanceString = str(round(percent * 100, 2)) + '%'
            message = 'success:' + name + ':' + performance + ':' + performanceString
            robot.wwiSendText(message)
            break
        else:
            message = "percent"
        message += ":" + str(percent)
        robot.wwiSendText(message)
        tx = t[0]
    if RECORD_ANIMATION:
        # Stops the simulation if the controller takes too much time
        step_counter += 1
        if step_counter >= step_max:
            break

if RECORD_ANIMATION:
    # Write performance to file, stop recording and close Webots
    rec.record_performance(running, percent)
    rec.animation_stop(robot, timestep)
    robot.simulationQuit(0)
else:
    benchmarkPerformance(message, robot)

robot.simulationSetMode(Supervisor.SIMULATION_MODE_PAUSE)
