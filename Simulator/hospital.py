import random
import simpy
import math

RANDOM_SEED = 42
NUM_DOCTORS = 2 
HEALTIME = 4
T_INTER = 2 
SIM_TIME = 720 #Goal is 12 hour window
ARRIVAL_RATE = 0.4

#WITHIOUT THE USE OF PREDICTOR DATA, HERE IS THE HOSPITAL METRICS WE WILL USE:
#http://emergencias.portalsemes.org/descargar/evidence-of-the-validity-of-the-emergency-severity-index-for-triage-in-a-general-hospital-emergency-department/force_download/
#USING THE ESI METRIC, OUR GLOBAL CHANCE OF BEING EACH VALUE WILL BE THE FOLLOWING
ESI1 = 0.7
ESI2 = 14.9
ESI3 = 36.6
ESI4 = 35.1
ESI5 = 12.7
#USING THE RESOURCE METRICS, WE GIVE THE FOLLOWING CHANCES FOR CONSUMING RESOURCES
ESI1_CONSUME_0 = 73.5
ESI1_CONSUME_1 = 16.3
ESI1_CONSUME_M = 10.2
ESI2_CONSUME_0 = 8.6
ESI2_CONSUME_1 = 82.1
ESI2_CONSUME_M = 9.3
ESI3_CONSUME_0 = 3.4
ESI3_CONSUME_1 = 11.6
ESI3_CONSUME_M = 85
ESI4_CONSUME_0 = 6.6
ESI4_CONSUME_1 = 8.2
ESI4_CONSUME_M = 82.2
ESI5_CONSUME_0 = 0
ESI5_CONSUME_1 = 0
ESI5_CONSUME_M = 100
#USING THE TIME METRICS, WE GIVE THE FOLLOWING TIME WITH STANDARD DEVIATION FOR THEIR STAY
#THESE TIME VALUES ARE IN MINUETS
ESI1_AVG_TIME = 476
ESI1_TIME_SD  = 228
ESI2_AVG_TIME = 716
ESI2_TIME_SD  = 659
ESI3_AVG_TIME = 333
ESI3_TIME_SD  = 259
ESI4_AVG_TIME = 176
ESI4_TIME_SD  = 110
ESI5_AVG_TIME = 166
ESI5_TIME_SD  = 93

ESI_CHANCE   = [ESI1, ESI2, ESI3, ESI4, ESI5]
ESI_CONSUME  = [[ESI1_CONSUME_0, ESI1_CONSUME_1, ESI1_CONSUME_M],
				[ESI2_CONSUME_0, ESI2_CONSUME_1, ESI2_CONSUME_M],
				[ESI3_CONSUME_0, ESI3_CONSUME_1, ESI3_CONSUME_M],
				[ESI4_CONSUME_0, ESI4_CONSUME_1, ESI4_CONSUME_M],
				[ESI5_CONSUME_0, ESI5_CONSUME_1, ESI5_CONSUME_M]]
ESI_TIME     = [[ESI1_AVG_TIME, ESI1_TIME_SD],
				[ESI2_AVG_TIME, ESI2_TIME_SD],
				[ESI3_AVG_TIME, ESI3_TIME_SD],
				[ESI4_AVG_TIME, ESI4_TIME_SD],
				[ESI5_AVG_TIME, ESI5_TIME_SD]]



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

    def new_wait(self, wait):
        self.curr_waits.append(wait)




class Hospital(object):
	#HERE WE WILL DEFINE THE ELEMENTS THAT THE HOSPITAL WILL HAVE
    def __init__(self, env, num_doctors, num_beds):
        self.env = env
        self.doctor = num_doctors
        self.beds = num_beds
        self.patients = [] #HERE WE NEED TO IMPLEMENT THE CARRY OVER PATIENTS BETWEEN HOSPITAL DAYS
      	self.bed_contents = []



    def check_in(self, patient, status):
        #yield self.env.timeout(WASHTIME)
        print("Checked " + patient + " in with status " + status)

    def heal(self, patient, bed_wait, status):
        yield self.env.timeout(HEALTIME) #+ bed_wait/2)
        print("healed " + patient + " in " +str(HEALTIME) + " seconds")  #+ bed_wait/2) + " seconds")

    def recieve_patient(self, env, patient):
    	cur_patient_esi = patient.status
    	i = 0
    	arr_len = self.patients.len()
    	while(i < arr_len):
    		if(cur_patient_esi < self.patients[i].status):
    			self.patients.insert(i, patient)
    			i = arr_len + 1
    		else:
    			i += 1
    	if(i == arr_len):
    		self.patients.append(patient)

#IMPORTANT#
#Currently there is a proplem with how hospital patients are catagorized, currenlty patient 5's will wait
#Forever as other patients of equal status are serviced

    def pass_time(self, env):
    	#pass_time will be the general function that can be used to sequence a minute
    	#Checking in on patients:
    	arr_len = self.bed_contents.len()
    	if(arr_len > 0):
    		i = 0
			d = 0 #Number of doctors in use    		
    		while(i < arr_len and d < self.doctor):
    			if(self.bed_contents[i].time_with_doc > 0)
    				d += 1
    				self.bed_contents[i].time_with_doc -= 1
    			i += 1
    	
    	#Remove healed patients
    	if(arr_len > 0):
    		i = 0
    		while(i < arr_len):
    			if(self.bed_contents[i].time_with_doc <= 0 and self.bed_contents[i].time_to_heal <= 0):
    				self.bed_contents[i].pop(i) #can be recorded if we want
    			else:
    				self.bed_contents[i].time_to_heal -= 1 #could overflow if patient waits for eternity 
    				i += 1
    				arr_len -= 1
    	
    	#Add new patients to beds
    	while(arr_len < self.beds and self.patients.len() > 0):
    		cur_patient_esi = self.patients[0].status
    		i = 0
    		#find where in bed order the patient belongs and place them there
    		#Will insert patient in ESI order with 1 being front, 5 beint in back
    		while(i < arr_len):
    			if(self.bed_contents[i].status < cur_patient_esi):
    				#Found spot to insert new patient into bed
    				self.bed_contents.insert(i, self.patients[0].pop())
    				arr_len += 1
    				i = arr_len + 1
    			else:
    				i += 1

    		#lowest classified case at the moment
    		if(i == arr_len):
    			self.bed_contents.append(self.patients[0].pop())


		





'''
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
'''

class patient(object):
	def __init__(self, env, status, consume, time_to_heal, arrival_time):
		self.env = env
		self.status = status
		self.consume = consume
		self.time_to_heal = time_to_heal
		self.time_with_doc = time_to_heal/4 #Using the source http://ugeskriftet.dk/files/scientific_article_files/2018-12/a4558.pdf
		self.arrival_time = arrival_time


class patient_generator(object):
	def __init__(self, env):
		self.env = env
		self.esi_chance  = ESI_CHANCE
		self.esi_consume = ESI_CONSUME
		self.esi_time    = ESI_TIME

	def make_patient(self, env):
		pat_esi = get_status()
		pat_com = get_consume(pat_esi)
		pat_tim = get_time(pat_esi)
		new_pat = patient(env, pat_esi, pat_com, pat_tim, env.now())
		return (new_pat)

	#The esi status of the patient upon them entering the hospital
	def get_status(self, env):
		i = 5
		while(i > 1):
			if(self.esi_chance[i - 1] < random.uniform((1,100), 2)):
				return i
			i - 1
		return 1

	#The amount of resources that the patient will consume during their visit
	def get_consume(self, env, esi):
		i = 3
		while(i > 1):
			if(self.esi_consume[esi - 1][i - 1] < random.uniform((1,100), 2)):
				return i
			i - 1
		return (self.esi_consume[esi - 1][0])

	#How much time that the patient will need in the bed in order to be discharged from the ER
	def get_time(self, env, esi):
		return (self.esi_time[esi - 1][0] + self.esi_time[esi - 1][1] * random.uniform((.5, 1.5), 3))


def setup(env, rec, num_doctors, num_beds, previous_patients):

    hospital = Hospital(env, num_doctors, num_beds)
    rec.new_history(num_doctors, num_beds)
    patient_generator(env)

    #This is where we will run the simulation loop
    #I'm writing this on 2 assumptions:
    #Each iteration of the while loop is one minute
    #Corvallis has the odds of 0.0477495 each minute of a patient showing up to the emergency department.
    i = 0
    while True:
    	patient_chance = random.random()
    	if(patient_chance < 0.0477495):
    		new_patient = patient_generator.make_patient(env)
    		hospital.recieve_patient(new_patient)
    	hospital.pass_time(env)
    	'''
        sin_value = (math.fabs(math.sin(env.now/200)))
        next_arrival_time =  sin_value * prng.exponential(1.0 / ARRIVAL_RATE) + 1
        print(str(sin_value) + " " + (str(next_arrival_time)  ))
        yield env.timeout(next_arrival_time)
        i += 1
        env.process(patient(env, rec, 'patient %d' % i, hospital, 0))
		'''

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


'''
HERE IS WHERE OUR PROGRAM IS ACTUALLY BEING RUN
Order of functions:

Record Object is initialized:
	Maintains record of hospitalized paitents and the time to help

Simulate Object:
	Simulate sets up simpy enviroment to equal the setup function
	Also takes in basic inputs for the simulation
	Have the process run until time is "up"

Setup:
	Takes basic inputs from simulate
	Initializes the Hospital 
	Randomly Generate patients for hospital forever
'''

rec = Record()
for i in range(1,4,1):
    for j in range(1,4,1):
        simulate(j, i, rec, SIM_TIME, [])

for thing in rec.history:
    print(thing)
