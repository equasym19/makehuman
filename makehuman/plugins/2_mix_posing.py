#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from core import G
import events3d
import bvh
import getpath
import animation
import log
import numpy as np

class MixPoseAdapter(events3d.EventHandler):
    def __init__(self):
        super(MixPoseAdapter, self).__init__()
        self.human = G.app.selectedHuman
        self.selectedFile = None
        self.selectedPose = None

        self._setting_pose = False

        self.sysDataPath = getpath.getSysDataPath('special_poses/mix/')
        self.userPath = getpath.getDataPath('special_poses/mix/')
        self.paths = [self.userPath, self.sysDataPath]
        if not os.path.exists(self.userPath):
            os.makedirs(self.userPath)


    def _get_current_pose(self):
        return self.human.getActiveAnimation()

    def _get_current_unmodified_pose(self):
        pose = self._get_current_pose()
        if pose and hasattr(pose, 'pose_mix_backref'):
            return pose.pose_mix_backref
        return pose

    def applyToPose(self, pose):
        self._setting_pose = True

        if self._get_current_pose() is None:
            # No pose set, simply set this one
            pose_ = pose
            pose_.pose_mix_backref = None
        else:
            org_pose = self._get_current_unmodified_pose()
            pose_ = animation.mixPoses(org_pose, pose, self.affected_bone_idxs)
            pose_.pose_foot_backref = org_pose

        pose_.name = 'special-mix-pose'
        self.human.addAnimation(pose_)
        self.human.setActiveAnimation('special-mix-pose')

        self.human.setPosed(True)
        self.human.refreshPose()

        self._setting_pose = False

    def loadMixPose(self, filename):
        log.debug("Loading special mix pose from %s", filename)
        self.selectedFile = filename
        if not filename:
            # Unload current pose
            self.selectedFile = None
            self.selectedPose = None
            # Remove the special pose from existing pose by restoring the original
            org_pose = self._get_current_unmodified_pose()
            if org_pose is None:
                self.human.setActiveAnimation(None)
            elif self.human.hasAnimation(org_pose.name):
                self.human.setActiveAnimation(org_pose.name)
            else:
                self.human.addAnimation(org_pose)
                self.human.setActiveAnimation(org_pose.name)

            # Remove pose reserved for ... pose library from human
            if self.human.hasAnimation('special-mix-pose'):
                self.human.removeAnimation('special-mix-pose')
            self.human.refreshPose(updateIfInRest=True)
            return

        # Load pose
        #bvh_file = animation.loadPoseFromMhpFile(filename,self.human.getBaseSkeleton()) #bvh.load(filename, convertFromZUp="auto")
        #anim = animation.loadPoseFromMhpFile(filename,self.human.getBaseSkeleton()) #bvh.load(filename, convertFromZUp="auto")
        skel=self.human.getBaseSkeleton()
        bvh_file = bvh.load(filename, convertFromZUp="auto")
        anim = bvh_file.createAnimationTrack(self.human.getBaseSkeleton())
        self.affected_bone_idxs=[]
        with open(filename[0:-4]+".bones") as fp:
            for line in fp:
                self.affected_bone_idxs.append(skel.getBone(line.strip('\n')).index)
        self.applyMixPose(anim)

    def applyMixPose(self, anim):
        self.selectedPose = anim
        if anim is None:
            self.selectedFile = None

        # Assign to human
        if anim:
            self.applyToPose(self.selectedPose)  # TODO override or add?
        self.human.refreshPose()

    def onHumanChanging(self, event):
        if event.change == 'reset':
            self._setting_pose = True
            self.selectedFile = None
            self.selectedPose = None

    def onHumanChanged(self, event):
        if event.change == 'proxyChange':
            if event.proxy != 'clothes':
                return
            proxy = event.proxy_obj
            if not proxy:
                return
            mix_pose = proxy.special_pose.get("mix", None)
            if not mix_pose:
                return
            filename = getpath.thoroughFindFile(mix_pose, self.paths)
            if not os.path.isfile(filename):
                log.error("Could not find a file for special_pose mix %s, file does not exist.", filename)
                return
            if event.action == 'add':
                self.loadMixPose(filename)
            elif event.action == 'remove':
                if self.selectedFile and getpath.isSamePath(filename, self.selectedFile):
                    self.loadMixPose(None)

        if event.change == 'poseChange' and not self._setting_pose:
            if self.selectedPose:
                self.applyMixPose(self.selectedPose)
        if event.change == 'reset':
            # Update GUI after reset (if tab is currently visible)
            self._setting_pose = False
            self.loadMixPose(None)


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements

def load(app):
    eventhandler = MixPoseAdapter()
    app.addEventHandler(eventhandler, 4310) # After pose and expression


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    pass
