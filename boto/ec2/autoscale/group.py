# Copyright (c) 2009-2011 Reza Lotun http://reza.lotun.name/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


from boto.ec2.elb.listelement import ListElement
from boto.resultset import ResultSet
from boto.ec2.autoscale.request import Request
from boto.ec2.autoscale.instance import Instance


class ProcessType(object):
    def __init__(self, connection=None):
        self.connection = connection
        self.process_name = None

    def __repr__(self):
        return 'ProcessType(%s)' % self.process_name

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'ProcessName':
            self.process_name = value


class SuspendedProcess(object):
    def __init__(self, connection=None):
        self.connection = connection
        self.process_name = None
        self.reason = None

    def __repr__(self):
        return 'SuspendedProcess(%s, %s)' % (self.process_name, self.reason)

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'ProcessName':
            self.process_name = value
        elif name == 'SuspensionReason':
            self.reason = value


class EnabledMetric(object):
    def __init__(self, connection=None, metric=None, granularity=None):
        self.connection = connection
        self.metric = metric
        self.granularity = granularity

    def __repr__(self):
        return 'EnabledMetric(%s, %s)' % (self.metric, self.granularity)

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'Granularity':
            self.granularity = value
        elif name == 'Metric':
            self.metric = value


class AutoScalingGroup(object):
    def __init__(self, connection=None, name=None,
                 launch_config=None,
                 availability_zones=None,
                 load_balancers=None, default_cooldown=None,
                 desired_capacity=None,
                 min_size=None, max_size=None, **kwargs):
        """
        Creates a new AutoScalingGroup with the specified name.

        You must not have already used up your entire quota of
        AutoScalingGroups in order for this call to be successful. Once the
        creation request is completed, the AutoScalingGroup is ready to be
        used in other calls.

        :type name: str
        :param name: Name of autoscaling group.

        :type launch_config: str
        :param launch_config: Name of launch configuration name.

        :type availability_zones: list
        :param availability_zones: List of availability zones.

        :type load_balancers: list
        :param load_balancers: List of load balancers.

        :type minsize: int
        :param minsize: Minimum size of group

        :type maxsize: int
        :param maxsize: Maximum size of group

        :type default_cooldown: int
        :param default_cooldown: Number of seconds after a Scaling Activity completes
                                 before any further scaling activities can start.

        :type desired_capacity: int
        :param desired_capacity: The desired capacity for the group.

        :rtype: :class:`boto.ec2.autoscale.group.AutoScalingGroup`
        :return: An autoscale group.
        """
        self.name = name or kwargs.get('group_name')   # backwards compatibility
        self.connection = connection
        self.min_size = int(min_size) if min_size is not None else None
        self.max_size = int(max_size) if max_size is not None else None
        self.created_time = None
        default_cooldown = default_cooldown or kwargs.get('cooldown')  # backwards compatibility
        self.default_cooldown = int(default_cooldown) if default_cooldown is not None else None
        self.launch_config = launch_config
        if self.launch_config:
            self.launch_config_name = self.launch_config.name
        else:
            self.launch_config_name = None
        self.desired_capacity = desired_capacity
        lbs = load_balancers or []
        self.load_balancers = ListElement(lbs)
        zones = availability_zones or []
        self.availability_zones = ListElement(zones)
        self.instances = None
        self.placement_group = None
        self.autoscaling_group_arn = None
        self.healthcheck_grace_period = None
        self.healthcheck_type = None
        self.vpc_zone_identifier = None

    # backwards compatible access to 'cooldown' param
    def _get_cooldown(self):
        return self.default_cooldown

    def _set_cooldown(self, val):
        self.default_cooldown = val
    cooldown = property(_get_cooldown, _set_cooldown)

    def __repr__(self):
        return 'AutoScalingGroup<%s>: created:%s, minsize:%s, maxsize:%s, capacity:%s' % (self.name,
                                                                                          self.created_time,
                                                                                          self.min_size,
                                                                                          self.max_size,
                                                                                          self.desired_capacity)

    def startElement(self, name, attrs, connection):
        if name == 'Instances':
            self.instances = ResultSet([('member', Instance)])
            return self.instances
        elif name == 'LoadBalancerNames':
            return self.load_balancers
        elif name == 'AvailabilityZones':
            return self.availability_zones
        elif name == 'EnabledMetrics':
            self.enabled_metrics = ResultSet([('member', EnabledMetric)])
        elif name == 'SuspendedProcesses':
            self.suspended_processes = ResultSet([('member', SuspendedProcess)])
        else:
            return

    def endElement(self, name, value, connection):
        if name == 'MinSize':
            self.min_size = int(value)
        elif name == 'AutoScalingGroupARN':
            self.autoscaling_group_arn = value
        elif name == 'CreatedTime':
            self.created_time = value
        elif name == 'DefaultCooldown':
            self.default_cooldown = int(value)
        elif name == 'LaunchConfigurationName':
            self.launch_config_name = value
        elif name == 'DesiredCapacity':
            self.desired_capacity = int(value)
        elif name == 'MaxSize':
            self.max_size = int(value)
        elif name == 'AutoScalingGroupName':
            self.name = value
        elif name == 'PlacementGroup':
            self.placement_group = value
        elif name == 'HealthCheckGracePeriod':
            self.healthcheck_grace_period = int(value)
        elif name == 'HealthCheckType':
            self.healthcheck_type = value
        elif name == 'VPCZoneIdentifier':
            self.vpc_zone_identifier = value
        else:
            setattr(self, name, value)

    def set_capacity(self, capacity):
        """ Set the desired capacity for the group. """
        params = {
                  'AutoScalingGroupName' : self.name,
                  'DesiredCapacity'      : capacity,
                 }
        req = self.connection.get_object('SetDesiredCapacity', params,
                                            Request)
        self.connection.last_request = req
        return req

    def update(self):
        """ Sync local changes with AutoScaling group. """
        return self.connection._update_group('UpdateAutoScalingGroup', self)

    def shutdown_instances(self):
        """ Convenience method which shuts down all instances associated with
        this group.
        """
        self.min_size = 0
        self.max_size = 0
        self.desired_capacity = 0
        self.update()

    def delete(self):
        """ Delete this auto-scaling group if no instances attached or no
        scaling activities in progress.
        """
        return self.connection.delete_auto_scaling_group(self.name)

    def get_activities(self, activity_ids=None, max_records=50):
        """
        Get all activies for this group.
        """
        return self.connection.get_all_activities(self, activity_ids, max_records)

    def suspend_processes(self, scaling_processes=None):
        """ Suspends Auto Scaling processes for an Auto Scaling group. """
        return self.connection.suspend_processes(self.name, scaling_processes)

    def resume_processes(self, scaling_processes=None):
        """ Resumes Auto Scaling processes for an Auto Scaling group. """
        return self.connection.resume_processes(self.name, scaling_processes)


class AutoScalingGroupMetric(object):
    def __init__(self, connection=None):

        self.connection = connection
        self.metric = None
        self.granularity = None

    def __repr__(self):
        return 'AutoScalingGroupMetric:%s' % self.metric

    def startElement(self, name, attrs, connection):
        return

    def endElement(self, name, value, connection):
        if name == 'Metric':
            self.metric = value
        elif name == 'Granularity':
            self.granularity = value
        else:
            setattr(self, name, value)

