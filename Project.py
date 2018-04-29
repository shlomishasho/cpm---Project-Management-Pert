import logging

# PERT implemtnion in python

#Tal Cohen : 308275429

#Shlomi Shasho: 308140557

class LogMixin (object):
    @property
    def logger(self):
        name = '.'.join([__name__, self.__class__.__name__])
        return logging.getLogger (name)

logging.basicConfig (level=logging.INFO, filename='PERT_log.log', filemode='w',
                     format='%(asctime)s : %(name)-10s - %(levelname)-5s - %(funcName)20s() : %(message)s')

class Activity (LogMixin):
    def __init__(self, id_act, name, duration=0, description=None):
        self.id = id_act
        self.name = name
        self.duration = duration
        self.description = description

        # Earliest start time.
        self._es = 0
        # Latest start time.
        self._ls = 0
        # The amount of time that the activity can be delayed without
        # increasing the overall project's duration.
        self._slacktime = 0
        self.to_nodes = []
        self.incoming_nodes = []
        self.logger.info ("New activity created :" + self.name + " duration: " + str (self.duration) + " description: ")

    def __str__(self):
        str_activity = 'Activity %d : %s , %d days' % (self.id, self.name, self.duration)
        self.logger.info (str_activity)
        return str_activity

    def __repr__(self):
        return "(Activity %d : %s , %d days)" % (self.id, self.name, self.duration)

    @property
    def es(self):
        return self._es

    @property
    def ls(self):
        return self._ls

    @property
    def slacktime(self):
        return self._slacktime

    @es.setter
    def es(self, es):
        if es >= 0:
            self._es = es
        else:
            self._es = 0
        self.logger.info ("activity: " + self.name + " es: " + str (self.es))
        pass

    @ls.setter
    def ls(self, ls):
        if ls >= 0:
            self._ls = ls
        else:
            self._es = 0
        self.logger.info ("activity: " + self.name + " ls: " + str (self.ls))
        pass

    @slacktime.setter
    def slacktime(self, slacktime):
        if slacktime >= 0:
            self._slacktime = slacktime
        else:
            self._slacktime = 0
        self.logger.info ("activity: " + self.name + " slacktime: " + str (self._slacktime))
        pass


class Project (LogMixin):
    def __init__(self, dic_project=None):
        # the dicationry is dicationry of Activity Object both for key and value
        if dic_project is None:
            dic_project = {}
        else:
            for k, v in dic_project.items():
                if not isinstance(Activity, k) or not isinstance(Activity,v):
                    self.logger.info("dicatonry must be with activity object, both for key and value " )
                    return
        self.logger.info("new Project was Created")
        self.dic_project = dic_project
        self._activityCounter = 0
        self.name_to_activity = {}
        self._duration = 0

    def add_activiy(self, name, duration):
        """ If the activity  "activity" is not in
            self.dic_project, a key "activty" with an empty
            list as a value is added to the dictionary.
            Otherwise nothing has to be done.
        """
        act = Activity (self._activityCounter, name, duration)
        self._activityCounter += 1
        if act not in self.dic_project:
            self.dic_project[act] = []
            self.name_to_activity[name] = act
        self.logger.info ("new activity was added " + str (act))

    def read_log_file(self):
        f = open('PERT_log.log')
        for i in f.readlines():
            print(i + "\n")

    def activity_in_graph(self, activity_name):
        """check if activity in dicatnory"""
        self.logger.info ("check if activity on graph for " + activity_name)
        if activity_name not in self.name_to_activity:
            self.logger.info ("activity " + activity_name + " is not on graph")
            return False
        self.logger.info ("activity " + activity_name + " is on graph")
        return True

    def add_edge(self, from_activityname, to_activityname=None):
        """add edge from from_activityname to : to_activityname
        between two activities can be multiple edges!"""

        self.logger.info ("adding edge between" + str ((from_activityname, to_activityname)))

        if not self.activity_in_graph (from_activityname) or not self.activity_in_graph (to_activityname):
            self.logger.info ("cant add edge- activtity isnt exist")
            return

        fromactivity = self.name_to_activity.get (from_activityname)
        to_activity = self.name_to_activity.get (to_activityname)

        if to_activity in fromactivity.to_nodes:
            self.logger.info ("allready has this edge")
            return

        fromactivity.to_nodes.append (to_activity)
        to_activity.incoming_nodes.append (fromactivity)
        self.update_list (fromactivity, to_activity)
        self.logger.info ("edge was added succefully")
        pass

    def update_list(self, *args):
        """update the list on the dicationry project to  speicif activity"""
        for activ in args:
            self.dic_project[activ] = list (set (activ.incoming_nodes + activ.to_nodes))
        pass

    def remove_activity(self, activitytoremove_name):
        """remove activity from graph """
        self.logger.info("remove activity" + activitytoremove_name)
        if not self.activity_in_graph (activitytoremove_name):
            self.logger.info("cant remove- acitivty doesnt exist in project")
            return

        activity_toremove = self.name_to_activity.get (activitytoremove_name)
        if activitytoremove_name == "end" or activitytoremove_name == "start":
            self.logger.info("cant remove the end or the start activity of the project")
            return

        for act in activity_toremove.to_nodes:
            if len (act.incoming_nodes) == 1:
                self.add_edge (activity_toremove.incoming_nodes[0].name, act.name)

        for act in self.dic_project[activity_toremove]:
            if activity_toremove in act.incoming_nodes:
                act.incoming_nodes.remove (activity_toremove)
            elif activity_toremove in act.to_nodes:
                act.to_nodes.remove (activity_toremove)
            self.update_list (act)

        del self.dic_project[activity_toremove]
        del self.name_to_activity[activity_toremove.name]
        self.logger.info ("acitivty: " + activitytoremove_name + "was removed succefully")

    def find_all_circles(self):
        """find circles from all the activites"""
        self.logger.info ("find all circles in graph")
        _circles_dic = {}
        for activ in self.dic_project.keys ():
            _circles_dic[activ.name] = self.find_all_paths (activ.name, activ.name, True)
        self.logger.info ("circles in graph :" + str (_circles_dic))
        return _circles_dic

    def find_all_paths(self, start_vertex, end_vertex, cycle_check=False, path=None):
        """ find all paths from start_vertex to end_vertex
            in graph
            if boolean cycleCheck is TRUE so try to look for circle and not a straight path
            Recursive function"""
        if path is None:
            path = []
        if not self.activity_in_graph (start_vertex) or not self.activity_in_graph (end_vertex):
            return None

        self.logger.info ("find path from " + start_vertex + " to: " + end_vertex)
        self.logger.info ("check for cycle?" + str (cycle_check))
        start_vertex_act = self.name_to_activity.get (start_vertex)
        end_vertex_act = self.name_to_activity.get (end_vertex)
        graph = self.dic_project
        path = path + [start_vertex_act.name]
        if start_vertex_act == end_vertex_act and not cycle_check:
            return [path]
        if start_vertex_act not in graph:
            return None

        paths = []
        for act in start_vertex_act.to_nodes:
            if act.name not in path or act == end_vertex_act:
                extended_paths = self.find_all_paths (act.name, end_vertex, False, path)
                if extended_paths:
                    paths += extended_paths
                # for p in extended_paths:
                #     paths.append(p)
        self.logger.info ("all paths are : " + str (paths))

        return paths

    def find_isolated(self):
        """find isolated activites: activites with no descending or asscending activites """
        self.logger.info ("find_isolated()")
        isolated__activities = []
        for activity in self.dic_project:
            if len (activity.incoming_nodes) == 0 or len (activity.to_nodes) == 0:
                isolated__activities.append (activity.name)
        self.logger.info ("isloated activites" + str (isolated__activities))
        return isolated__activities


    def find_critical_path(self, start_vertex, end_vertex):
        #     return "critical path is from the first activity to the end"
        if not self.activity_in_graph (start_vertex) or not self.activity_in_graph (end_vertex):
            return None

        self.logger.info (f"find_critical_path({start_vertex},{end_vertex})")
        all_paths = self.find_all_paths (start_vertex, end_vertex)
        durations_list = list (map (self.calculate_duration, all_paths))
        if durations_list:
            max_duration = max (durations_list)
            max_loc = durations_list.index (max_duration)
            crit_path_list = [(node, self.name_to_activity.get (node).duration) for node in all_paths[max_loc]]
        else:
            crit_path_list = None
        self.logger.info ("critical path is " + str (crit_path_list))
        return crit_path_list

    @property
    def duration(self):
        """duration of all project by the critical path """
        critical = self.find_critical_path ("start", "end")
        crit = [path[0] for path in critical]
        self._duration = self.calculate_duration (crit)
        self.logger.info ("self.duration" + str (self._duration))
        return self._duration

    def calculate_duration(self, path):
        """calculate duration to a given path
            path is a list of activity names"""
        self.logger.info ("calculate_duration of a path " + str (path))
        sum_duration = 0
        for vertex_name in path:
            act = self.name_to_activity.get (vertex_name)
            sum_duration += act.duration
        self.logger.info ("calculate_duration() of a path " + str (path) + ": " + str (sum_duration))
        return sum_duration

    def find_es(self, start_activity):
        """update the earlist_time to start each activity"""
        self.logger.info (f"find_es({start_activity})")
        isolated_list = self.find_isolated ()
        for act in self.dic_project:
            if act.name not in isolated_list or act.name == "end":
                critical_temp = self.find_critical_path (start_activity, act.name)
                crit = [path[0] for path in critical_temp]
                act.es = self.calculate_duration (crit) - act.duration
            else:
                act.es = 0
            self.logger.info ("activity:" + act.name + " es : " + str (act.es))
        pass

    def find_ls(self, start_activity):
        """find the latest time to start each activity"""
        self.logger.info (f"find_es({start_activity})")
        isolated_list = self.find_isolated ()
        for act in self.dic_project:
            if act.name not in isolated_list or act.name == "start":
                critical_temp = self.find_critical_path (start_activity, act.name)
                crit = [path[0] for path in critical_temp]
                act.ls = self._duration - (self.calculate_duration (crit))
            else:
                act.ls = self._duration - act.duration
            self.logger.info ("activity:" + act.name + " ls : " + str (act.ls))
        pass

    def change_direction(self):
        """change the direction of the graph
        use only in function calculate_slack_time() """
        self.logger.info ("change_direction()")
        for act in self.dic_project:
            temp = act.incoming_nodes
            act.incoming_nodes = act.to_nodes
            act.to_nodes = temp


    def exist_circles(self):
        """check if there is circles in the project"""
        check = False
        if not self.find_all_circles():
            check = True
        self.logger.info("exist circles " + str(check))
        return check

    def calculate_slack_time(self):
        """calculate the slack time for all activities
        note : cant calculate slack time if there are circles in the graph"""
        self.logger.info ("calculate_slack_time()")
        if self.exist_circles():
            self.logger.info ("there are cycles in the graph, cant calculate slack time .. return ")
            return

        self.find_es ("start")
        duration = self.duration
        self.change_direction ()
        self.find_ls ("end")
        self.change_direction ()

        for activ_to_calculate in self.dic_project:
            activ_to_calculate.slacktime = activ_to_calculate.ls - activ_to_calculate.es
        slacktime_list = ([(node, node.slacktime) for node in self.dic_project if node.slacktime is not 0])
        slacktime_list.sort (key=lambda x: x[1])
        self.logger.info ("slack time calculated: " + str (slacktime_list))
        return slacktime_list

    def __str__(self):
        project_string ="-names of activites in project: \n"+str(self.name_to_activity.keys())
        project_string += "\n -all edges  in project :\n"
        for k in self.dic_project.keys():
            for v in k.to_nodes:
                project_string+="("+str(k)+")---->("+str(v)+")\n"

        # project_string = "-all activites in project :\n" + str (self.dic_project)
        project_string += "\n-paths from start to end : \n" + str (self.find_all_paths ("start", "end"))
        circles = self.find_all_circles ()
        if not circles:
            project_string += "\n Circles in graph: \n" + str (circles)
        else:
            project_string += "\n-There are no Circles in Graph"
            project_string += "\n-Total duration of Project: " + str (self.duration)
            project_string += "\n-critical path in the project: \n" + str(self.find_critical_path("start", "end"))
            slacklist = self.calculate_slack_time ()
            project_string += "\n-slack time by descending order ( without critical path nodes) :\n" + str (slacklist)
            self.logger.info(project_string)

        return project_string


if __name__ == "__main__":
# assuming that the project start with start activity , end with end activity - Mica's order
    p = Project()
    p.add_activiy ("start", 2)
    p.add_activiy ("A", 1)
    p.add_activiy ("B", 3)
    p.add_activiy ("C", 12)
    p.add_activiy ("D", 2)
    p.add_activiy ("E", 1)
    p.add_activiy ("F", 6)
    p.add_activiy ("end", 2)

    # The Project Dicationary: (activity,name,duration)
    # {(Activity 0: start, 2 days): [], (Activity 1: A, 1 days): [], (Activity 2: B, 3 days): [],
    #  (Activity 3: C, 12 days): [], (Activity 4: D, 2 days): [], (Activity 5: E, 1 days): [],
    #  (Activity 6: F, 6 days): [], (Activity 7: end, 2 days): []}

    p.add_edge("start", "A")
    p.add_edge ("start", "D")
    p.add_edge ("start", "F")
    p.add_edge ("A", "B")
    p.add_edge ("B", "C")
    p.add_edge ("B", "E")
    p.add_edge ("D", "E")
    p.add_edge ("C", "end")
    p.add_edge ("E", "end")
    p.add_edge ("F", "end")
    print ()
    print (p)

    # read from lof file and print
    # p.read_log_file()

    # case of add activity and remove
    # print ()
    # p.add_activiy("S",1)
    # p.add_edge("S","F")
    # print(p)
    # print ()
    # p.remove_activity("S")
    # print(p)



