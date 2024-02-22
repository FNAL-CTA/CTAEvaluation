#! /usr/bin/env python3

from SQAReflection import ReflectedBase, EnstoreReflected


class EnstoreVolume(EnstoreReflected, ReflectedBase):
    __tablename__ = "volume"


class EnstoreFile(EnstoreReflected, ReflectedBase):
    __tablename__ = "file"
