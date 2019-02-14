import random
import simpy
import math

RANDOM_SEED = 42
NUM_DOCTORS = 2 
HEALTIME = 4
T_INTER = 2 
SIM_TIME = 20
ARRIVAL_RATE = 0.4

import numpy as np
from numpy.random import RandomState
RNG_SEED = 6354
prng = RandomState(RNG_SEED)

class Record(object):
    def __init__(self):
        self.doctors = 0
        self.beds = 0
        self.patients = 0
        self.curr_waits = []
        self.history = []

    def new_history(self, new_docs, new_beds):
        if (len(self.curr_waits) > 0):
            self.history.append((self.patients, len(self.curr_waits), self.doctors, self.beds, self.curr_waits))
            self.curr_waits = []
        self.doctors = new_docs
        self.beds = new_beds
        self.patients = 0

    def new_patient(self):
        self.patients += 1


#Adding status to value
    def new_wait(self, wait):
        self.curr_waits.append(wait)


class Hospital(object):
	#HERE WE WILL DEFINE THE ELEMENTS THAT THE HOSPITAL WILL AHVE
    def __init__(self, env, num_doctors, num_beds):
        self.env = env
        self.doctor = simpy.Resource(env, num_doctors)
        self.beds = simpy.Resource(env, num_beds)

    def check_in(self, patient, status):
        #yield self.env.timeout(WASHTIME)
        print("Checked " + patient + " in with status " + status)

    def heal(self, patient, bed_wait, status):
        yield self.env.timeout(HEALTIME) #+ bed_wait/2)
        print("healed " + patient + " in " +str(HEALTIME) + " seconds")  #+ bed_wait/2) + " seconds")

def patient(env, rec, name, hos, status):
    print('%s enters the hospital at %.2f.' % (name, env.now))
    rec.new_patient()
    arrive = env.now
    bed_arrive = 0
    doctor_arrive = 0
    heal_arrive = 0
    status = 0

    bed_wait = 0
    heal_wait = 0    
    total_wait = 0

    with hos.beds.request() as bed_request:
        yield bed_request
        bed_arrive = env.now 
        bed_wait = env.now - arrive
        print('%s gets in a bed at %.2f.' % (name, bed_arrive))
        with hos.doctor.request() as doctor_request:
            yield doctor_request
            doctor_arrive = env.now
            doctor_wait = env.now - bed_arrive
            yield env.process(hos.heal(name, bed_arrive, 0))
            heal_wait = env.now - doctor_arrive
            heal_arrive = env.now
    total_wait = int(bed_wait + doctor_wait +heal_wait )
    rec.new_wait(total_wait)
    
    print('Arrive: %i bed_arrive: %i doctor_arrive: %i heal_arrive: %i' % (arrive, bed_arrive, doctor_arrive,heal_arrive))
    print('Bed wait: %i doctor wait %i heal wait: %i '  % (bed_wait, doctor_wait, heal_wait))
    print('%s leaves the hospital at %.2f.'  % (name, env.now))

def setup(env, rec, num_doctors, num_beds, previous_patients):

    hospital = Hospital(env, num_doctors, num_beds)
    rec.new_history(num_doctors, num_beds)

    i = 0
    while True:
        sin_value = (math.fabs(math.sin(env.now/200)))
        next_arrival_time =  sin_value * prng.exponential(1.0 / ARRIVAL_RATE) + 1
        print(str(sin_value) + " " + (str(next_arrival_time)  ))
        yield env.timeout(next_arrival_time)
        i += 1
        env.process(patient(env, rec, 'patient %d' % i, hospital, 0))

def simulate(num_doctors, num_beds, rec, sim_time, previous_patients):
	print('Hospital')
	random.seed(RANDOM_SEED)  

	env = simpy.Environment()
	env.process(setup(env, rec, num_doctors, num_beds, previous_patients))
	
	print("*")
	print("Starting  Doctors: " + str(num_doctors) + " Beds: " + str(num_beds))
	env.run(until=sim_time)
	print("Finishing Doctors: " + str(num_doctors) + " Beds: " + str(num_beds))
	print("*")


#Run the hosptial simulation for doctor 1-4 and bed values 1-4
rec = Record()
for i in range(1,4,1):
    for j in range(1,4,1):
        simulate(j, i, rec, SIM_TIME, [])

for thing in rec.history:
    print(thing)
