import simpy
import random
import statistics

#---------------START OF CHANGING INPUT VARIABLES---------------
numberOfCNCMachines = 5
numberOfMoldingMachines = 5
numberOfAssemblyStations = 5
numberOfInspectionStations = 5
numberOfPackagingStations = 5
lengthOfWorkShift = 480
totalShift = lengthOfWorkShift * 3
simulationTime = totalShift * 10

loadingTime = 2
machiningTime = 7
moldingTime = 5
assemblingTime = 6
inspectingTime = 2
packagingTime = 3

CNCFailRate = 0.001
CNCRepairTime = 30
moldingFailRate = 0.00125
moldingRepairTime = 25
assemblyFailRate = 0.00083
assemblyRepairTime = 20
#---------------END OF CHANGING INPUT VARIABLES---------------

totalFinished = 0
machiningTimes = []
moldingTimes = []
assemblyTimes = []
inspectingTimes = []
packagingTimes = []

#---------------RAW MATERIAL LOAD FUNCTION---------------
def loading(env, name, rawMaterialQueue):
    while True:
        yield env.timeout(loadingTime)
        print(f'{name} Raw materials loaded at {env.now:.2f}')
        yield rawMaterialQueue.put(1)

#---------------MACHINING FUNCTION---------------
def machining(env, name, rawMaterialQueue, cncMachines, machiningOutput):
    while True:
        yield rawMaterialQueue.get()
        with cncMachines.request() as request:
            yield request
            start_time = env.now
            yield env.timeout(machiningTime)
            machiningTimes.append(env.now - start_time)
            print(f'{name} Machining finished at {env.now:.2f}')
            yield machiningOutput.put(1)

#---------------MOLDING FUNCTION---------------
def molding(env, name, machiningOutput, moldingMachines, moldingOutput):
    while True:
        yield machiningOutput.get()
        with moldingMachines.request() as request:
            yield request
            start_time = env.now
            yield env.timeout(moldingTime)
            moldingTimes.append(env.now - start_time)
            print(f'{name} Molding finished at {env.now:.2f}')
            yield moldingOutput.put(1)

#---------------ASSEMBLING FUNCTION---------------
def assembling(env, name, moldingOutput, assemblyStations, assemblyOutput):
    while True:
        yield moldingOutput.get()
        with assemblyStations.request() as request:
            yield request
            start_time = env.now
            yield env.timeout(assemblingTime)
            assemblyTimes.append(env.now - start_time)
            print(f'{name} Assembling finished at {env.now:.2f}')
            yield assemblyOutput.put(1)

#---------------INSPECTING FUNCTION---------------
def inspecting(env, name, assemblyOutput, inspectionStations, inspectionOutput):
    while True:
        yield assemblyOutput.get()
        with inspectionStations.request() as request:
            yield request
            start_time = env.now
            yield env.timeout(inspectingTime)
            inspectingTimes.append(env.now - start_time)
            print(f'{name} Inspecting finished at {env.now:.2f}')
            yield inspectionOutput.put(1)

#---------------PACKAGING FUNCTION---------------
def packaging(env, name, inspectionOutput, packagingStations):
    global totalFinished
    while True:
        yield inspectionOutput.get()
        with packagingStations.request() as request:
            yield request
            start_time = env.now
            yield env.timeout(packagingTime)
            packagingTimes.append(env.now - start_time)
            totalFinished += 1
            print(f'{name} Packaging finished at {env.now:.2f}')

#---------------FUNCTION FOR SIMULATING THE FAILURE OF MACHINES---------------
def machineFail(env, name, machines, failRate, repairTime):
    while True:
        yield env.timeout(random.expovariate(failRate))
        with machines.request() as request:
            yield request
            print(f'{name} Machine failed at {env.now:.2f}')
            yield env.timeout(repairTime)
            print(f'{name} Repaired at {env.now:.2f}')

def startSimulation():
    global totalFinished
    totalFinished = 0

    random.seed()
    env = simpy.Environment()

    rawMaterialQueue = simpy.Store(env)
    machiningOutput = simpy.Store(env)
    moldingOutput = simpy.Store(env)
    assemblyOutput = simpy.Store(env)
    inspectionOutput = simpy.Store(env)

    cncMachines = simpy.Resource(env, capacity=numberOfCNCMachines)
    moldingMachines = simpy.Resource(env, capacity=numberOfMoldingMachines)
    assemblyStations = simpy.Resource(env, capacity=numberOfAssemblyStations)
    inspectionStations = simpy.Resource(env, capacity=numberOfInspectionStations)
    packagingStations = simpy.Resource(env, capacity=numberOfPackagingStations)

    for i in range(1, 11):
        env.process(loading(env, f'Loader - {i} ', rawMaterialQueue))
        env.process(machining(env, f'Machinist - {i} ', rawMaterialQueue, cncMachines, machiningOutput))
        env.process(molding(env, f'Molder - {i} ', machiningOutput, moldingMachines, moldingOutput))
        env.process(assembling(env, f'Assembler - {i} ', moldingOutput, assemblyStations, assemblyOutput))
        env.process(inspecting(env, f'Inspector - {i} ', assemblyOutput, inspectionStations, inspectionOutput))
        env.process(packaging(env, f'Packer - {i} ', inspectionOutput, packagingStations))

    env.process(machineFail(env, 'CNC Machine ', cncMachines, CNCFailRate, CNCRepairTime))
    env.process(machineFail(env, 'Molding Machine ', moldingMachines, moldingFailRate, moldingRepairTime))
    env.process(machineFail(env, 'Assembly Station ', assemblyStations, assemblyFailRate, assemblyRepairTime))

    env.run(until=simulationTime)

    print('\nSimulation Results:')
    print(f'Total Finished Products: {totalFinished}')
    print(f'Average Machining Time: {statistics.mean(machiningTimes):.2f} Minutes')
    print(f'Average Molding Time: {statistics.mean(moldingTimes):.2f} Minutes')
    print(f'Average Assembling Time: {statistics.mean(assemblyTimes):.2f} Minutes')
    print(f'Average Inspecting Time: {statistics.mean(inspectingTimes):.2f} Minutes')
    print(f'Average Packaging Time: {statistics.mean(packagingTimes):.2f} Minutes')

if __name__ == '__main__':
    startSimulation()
