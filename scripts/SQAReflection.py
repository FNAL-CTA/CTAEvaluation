#! /usr/bin/env python3

from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import DeclarativeBase


class ReflectedBase(DeclarativeBase):
    pass


class EnstoreReflected(DeferredReflection):
    __abstract__ = True


class CTAReflected(DeferredReflection):
    __abstract__ = True
