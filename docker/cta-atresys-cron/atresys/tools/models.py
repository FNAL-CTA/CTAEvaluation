from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, CHAR, CheckConstraint, Column, DateTime, Enum, ForeignKeyConstraint, Index, Integer, LargeBinary, Numeric, PrimaryKeyConstraint, SmallInteger, String, Table, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class AdminUser(Base):
    __tablename__ = 'admin_user'
    __table_args__ = (
        PrimaryKeyConstraint('admin_user_name', name='admin_user_pk'),
        Index('admin_user_aun_ci_un_idx', unique=True)
    )

    admin_user_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))


t_cta_catalogue = Table(
    'cta_catalogue', Base.metadata,
    Column('schema_version_major', Numeric(20, 0), nullable=False),
    Column('schema_version_minor', Numeric(20, 0), nullable=False),
    Column('next_schema_version_major', Numeric(20, 0)),
    Column('next_schema_version_minor', Numeric(20, 0)),
    Column('status', String(100)),
    Column('is_production', CHAR(1), nullable=False, server_default=text("'0'::bpchar")),
    CheckConstraint("is_production = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='cta_catalogue_ip_bool_ck'),
    CheckConstraint("next_schema_version_major IS NULL AND next_schema_version_minor IS NULL AND status::text = 'PRODUCTION'::text OR status::text = 'UPGRADING'::text", name='catalogue_status_content_ck')
)


t_databasechangelog = Table(
    'databasechangelog', Base.metadata,
    Column('id', String(255), nullable=False),
    Column('author', String(255), nullable=False),
    Column('filename', String(255), nullable=False),
    Column('dateexecuted', DateTime, nullable=False),
    Column('orderexecuted', Integer, nullable=False),
    Column('exectype', String(10), nullable=False),
    Column('md5sum', String(35)),
    Column('description', String(255)),
    Column('comments', String(255)),
    Column('tag', String(255)),
    Column('liquibase', String(20)),
    Column('contexts', String(255)),
    Column('labels', String(255)),
    Column('deployment_id', String(10))
)


class Databasechangeloglock(Base):
    __tablename__ = 'databasechangeloglock'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='databasechangeloglock_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    locked: Mapped[bool] = mapped_column(Boolean)
    lockgranted: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    lockedby: Mapped[Optional[str]] = mapped_column(String(255))


class DiskInstance(Base):
    __tablename__ = 'disk_instance'
    __table_args__ = (
        PrimaryKeyConstraint('disk_instance_name', name='disk_instance_pk'),
        Index('disk_instance_din_ci_un_idx', unique=True)
    )

    disk_instance_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    disk_instance_space: Mapped[List['DiskInstanceSpace']] = relationship('DiskInstanceSpace', back_populates='disk_instance')
    requester_activity_mount_rule: Mapped[List['RequesterActivityMountRule']] = relationship('RequesterActivityMountRule', back_populates='disk_instance')
    requester_group_mount_rule: Mapped[List['RequesterGroupMountRule']] = relationship('RequesterGroupMountRule', back_populates='disk_instance')
    requester_mount_rule: Mapped[List['RequesterMountRule']] = relationship('RequesterMountRule', back_populates='disk_instance')
    virtual_organization: Mapped[List['VirtualOrganization']] = relationship('VirtualOrganization', back_populates='disk_instance')
    archive_file: Mapped[List['ArchiveFile']] = relationship('ArchiveFile', back_populates='disk_instance')


class DriveConfig(Base):
    __tablename__ = 'drive_config'
    __table_args__ = (
        PrimaryKeyConstraint('key_name', 'drive_name', name='drive_config_dn_pk'),
    )

    drive_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    category: Mapped[str] = mapped_column(String(100))
    key_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(1000))
    source: Mapped[str] = mapped_column(String(100))


class DriveState(Base):
    __tablename__ = 'drive_state'
    __table_args__ = (
        CheckConstraint("desired_force_down = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='drive_dfd_bool_ck'),
        CheckConstraint("desired_up = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='drive_du_bool_ck'),
        CheckConstraint("drive_status::text = ANY (ARRAY['DOWN'::character varying, 'UP'::character varying, 'PROBING'::character varying, 'STARTING'::character varying, 'MOUNTING'::character varying, 'TRANSFERING'::character varying, 'UNLOADING'::character varying, 'UNMOUNTING'::character varying, 'DRAININGTODISK'::character varying, 'CLEANINGUP'::character varying, 'SHUTDOWN'::character varying, 'UNKNOWN'::character varying]::text[])", name='drive_ds_string_ck'),
        CheckConstraint("mount_type::text = ANY (ARRAY['NO_MOUNT'::character varying, 'ARCHIVE_FOR_USER'::character varying, 'ARCHIVE_FOR_REPACK'::character varying, 'RETRIEVE'::character varying, 'LABEL'::character varying, 'ARCHIVE_ALL_TYPES'::character varying]::text[])", name='drive_mt_string_ck'),
        CheckConstraint("next_mount_type::text = ANY (ARRAY['NO_MOUNT'::character varying, 'ARCHIVE_FOR_USER'::character varying, 'ARCHIVE_FOR_REPACK'::character varying, 'RETRIEVE'::character varying, 'LABEL'::character varying, 'ARCHIVE_ALL_TYPES'::character varying]::text[])", name='drive_nmt_string_ck'),
        PrimaryKeyConstraint('drive_name', name='drive_dn_pk'),
        Index('drive_state_dn_ci_un_idx', unique=True)
    )

    drive_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    host: Mapped[str] = mapped_column(String(100))
    logical_library: Mapped[str] = mapped_column(String(100))
    mount_type: Mapped[str] = mapped_column(String(100), server_default=text("'NO_MOUNT'::character varying"))
    drive_status: Mapped[str] = mapped_column(String(100), server_default=text("'UNKNOWN'::character varying"))
    desired_up: Mapped[str] = mapped_column(CHAR(1), server_default=text("'0'::bpchar"))
    desired_force_down: Mapped[str] = mapped_column(CHAR(1), server_default=text("'0'::bpchar"))
    next_mount_type: Mapped[str] = mapped_column(String(100), server_default=text("'NO_MOUNT'::character varying"))
    session_id: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    bytes_transfered_in_session: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    files_transfered_in_session: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    session_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    session_elapsed_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    mount_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    transfer_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    unload_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    unmount_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    draining_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    down_or_up_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    probe_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    cleanup_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    start_start_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    shutdown_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    reason_up_down: Mapped[Optional[str]] = mapped_column(String(1000))
    current_vid: Mapped[Optional[str]] = mapped_column(String(100))
    cta_version: Mapped[Optional[str]] = mapped_column(String(100))
    current_priority: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    current_activity: Mapped[Optional[str]] = mapped_column(String(100))
    current_tape_pool: Mapped[Optional[str]] = mapped_column(String(100))
    next_vid: Mapped[Optional[str]] = mapped_column(String(100))
    next_priority: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    next_activity: Mapped[Optional[str]] = mapped_column(String(100))
    next_tape_pool: Mapped[Optional[str]] = mapped_column(String(100))
    dev_file_name: Mapped[Optional[str]] = mapped_column(String(100))
    raw_library_slot: Mapped[Optional[str]] = mapped_column(String(100))
    current_vo: Mapped[Optional[str]] = mapped_column(String(100))
    next_vo: Mapped[Optional[str]] = mapped_column(String(100))
    user_comment: Mapped[Optional[str]] = mapped_column(String(1000))
    creation_log_user_name: Mapped[Optional[str]] = mapped_column(String(100))
    creation_log_host_name: Mapped[Optional[str]] = mapped_column(String(100))
    creation_log_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_update_host_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_update_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    disk_system_name: Mapped[Optional[str]] = mapped_column(String(100))
    reserved_bytes: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    reservation_session_id: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))


class MediaType(Base):
    __tablename__ = 'media_type'
    __table_args__ = (
        PrimaryKeyConstraint('media_type_id', name='media_type_pk'),
        Index('media_type_mtn_ci_un_idx', unique=True),
        Index('media_type_mtn_un_idx', 'media_type_name', unique=True)
    )

    media_type_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    media_type_name: Mapped[str] = mapped_column(String(100))
    cartridge: Mapped[str] = mapped_column(String(100))
    capacity_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    primary_density_code: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(3, 0))
    secondary_density_code: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(3, 0))
    nb_wraps: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 0))
    min_lpos: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    max_lpos: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))

    tape: Mapped[List['Tape']] = relationship('Tape', back_populates='media_type')


class MountPolicy(Base):
    __tablename__ = 'mount_policy'
    __table_args__ = (
        PrimaryKeyConstraint('mount_policy_name', name='mount_policy_pk'),
        Index('mount_policy_mpn_ci_un_idx', unique=True)
    )

    mount_policy_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    archive_priority: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    archive_min_request_age: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    retrieve_priority: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    retrieve_min_request_age: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    requester_activity_mount_rule: Mapped[List['RequesterActivityMountRule']] = relationship('RequesterActivityMountRule', back_populates='mount_policy')
    requester_group_mount_rule: Mapped[List['RequesterGroupMountRule']] = relationship('RequesterGroupMountRule', back_populates='mount_policy')
    requester_mount_rule: Mapped[List['RequesterMountRule']] = relationship('RequesterMountRule', back_populates='mount_policy')


class PhysicalLibrary(Base):
    __tablename__ = 'physical_library'
    __table_args__ = (
        CheckConstraint("is_disabled = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='physical_library_id_bool_ck'),
        PrimaryKeyConstraint('physical_library_id', name='physical_library_pk'),
        Index('physical_library_pln_ci_un_idx', unique=True)
    )

    physical_library_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    physical_library_name: Mapped[str] = mapped_column(String(100))
    physical_library_manufacturer: Mapped[str] = mapped_column(String(100))
    physical_library_model: Mapped[str] = mapped_column(String(100))
    nb_physical_cartridge_slots: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    nb_physical_drive_slots: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    is_disabled: Mapped[str] = mapped_column(CHAR(1), server_default=text("'0'::bpchar"))
    physical_library_type: Mapped[Optional[str]] = mapped_column(String(100))
    gui_url: Mapped[Optional[str]] = mapped_column(String(1000))
    webcam_url: Mapped[Optional[str]] = mapped_column(String(1000))
    physical_location: Mapped[Optional[str]] = mapped_column(String(100))
    nb_available_cartridge_slots: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[Optional[str]] = mapped_column(String(1000))
    disabled_reason: Mapped[Optional[str]] = mapped_column(String(1000))

    logical_library: Mapped[List['LogicalLibrary']] = relationship('LogicalLibrary', back_populates='physical_library')


class RepackStatusProd(Base):
    __tablename__ = 'repack_status_prod'
    __table_args__ = (
        PrimaryKeyConstraint('tape', name='repack_status_prod_pkey'),
    )

    tape: Mapped[str] = mapped_column(String(20), primary_key=True)
    entered: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=0))
    files: Mapped[int] = mapped_column(BigInteger)
    bytes: Mapped[int] = mapped_column(BigInteger)
    usage: Mapped[int] = mapped_column(SmallInteger)
    mode: Mapped[str] = mapped_column(Enum('auto', 'manual', 'error', name='automation_modes'))
    priority: Mapped[int] = mapped_column(SmallInteger)
    mediatype: Mapped[str] = mapped_column(String(20))
    tapepool: Mapped[str] = mapped_column(String(200))
    responsible: Mapped[str] = mapped_column(String(40))
    started: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    repacked: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    quarantined: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    reclaimed: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    finished: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    last_write_date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))


class DiskInstanceSpace(Base):
    __tablename__ = 'disk_instance_space'
    __table_args__ = (
        ForeignKeyConstraint(['disk_instance_name'], ['disk_instance.disk_instance_name'], name='disk_instance_space_din_fk'),
        PrimaryKeyConstraint('disk_instance_name', 'disk_instance_space_name', name='disk_instance_space_pk'),
        Index('disk_instance_space_disn_ci_un_idx', unique=True),
        Index('disk_instance_space_disn_un_idx', 'disk_instance_space_name', unique=True)
    )

    disk_instance_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    disk_instance_space_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    free_space_query_url: Mapped[str] = mapped_column(String(1000))
    refresh_interval: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_refresh_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    free_space: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    disk_instance: Mapped['DiskInstance'] = relationship('DiskInstance', back_populates='disk_instance_space')
    disk_system: Mapped[List['DiskSystem']] = relationship('DiskSystem', back_populates='disk_instance_space')


class LogicalLibrary(Base):
    __tablename__ = 'logical_library'
    __table_args__ = (
        CheckConstraint("is_disabled = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='logical_library_id_bool_ck'),
        ForeignKeyConstraint(['physical_library_id'], ['physical_library.physical_library_id'], name='logical_library_pli_fk'),
        PrimaryKeyConstraint('logical_library_id', name='logical_library_pk'),
        Index('logical_library_lln_ci_un_idx', unique=True),
        Index('logical_library_lln_un_idx', 'logical_library_name', unique=True),
        Index('logical_library_pli_idx', 'physical_library_id')
    )

    logical_library_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    logical_library_name: Mapped[str] = mapped_column(String(100))
    is_disabled: Mapped[str] = mapped_column(CHAR(1), server_default=text("'0'::bpchar"))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    disabled_reason: Mapped[Optional[str]] = mapped_column(String(1000))
    physical_library_id: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))

    physical_library: Mapped[Optional['PhysicalLibrary']] = relationship('PhysicalLibrary', back_populates='logical_library')
    tape: Mapped[List['Tape']] = relationship('Tape', back_populates='logical_library')


class RequesterActivityMountRule(Base):
    __tablename__ = 'requester_activity_mount_rule'
    __table_args__ = (
        ForeignKeyConstraint(['disk_instance_name'], ['disk_instance.disk_instance_name'], name='rqster_act_rule_din_fk'),
        ForeignKeyConstraint(['mount_policy_name'], ['mount_policy.mount_policy_name'], name='rqster_act_rule_mnt_plc_fk'),
        PrimaryKeyConstraint('disk_instance_name', 'requester_name', 'activity_regex', name='rqster_act_rule_pk'),
        Index('req_act_mnt_rule_din_idx', 'disk_instance_name'),
        Index('req_act_mnt_rule_mpn_idx', 'mount_policy_name')
    )

    disk_instance_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    requester_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    activity_regex: Mapped[str] = mapped_column(String(100), primary_key=True)
    mount_policy_name: Mapped[str] = mapped_column(String(100))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    disk_instance: Mapped['DiskInstance'] = relationship('DiskInstance', back_populates='requester_activity_mount_rule')
    mount_policy: Mapped['MountPolicy'] = relationship('MountPolicy', back_populates='requester_activity_mount_rule')


class RequesterGroupMountRule(Base):
    __tablename__ = 'requester_group_mount_rule'
    __table_args__ = (
        ForeignKeyConstraint(['disk_instance_name'], ['disk_instance.disk_instance_name'], name='rqster_grp_rule_din_fk'),
        ForeignKeyConstraint(['mount_policy_name'], ['mount_policy.mount_policy_name'], name='rqster_grp_rule_mnt_plc_fk'),
        PrimaryKeyConstraint('disk_instance_name', 'requester_group_name', name='rqster_grp_rule_pk'),
        Index('req_grp_mnt_rule_din_idx', 'disk_instance_name'),
        Index('req_grp_mnt_rule_mpn_idx', 'mount_policy_name')
    )

    disk_instance_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    requester_group_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    mount_policy_name: Mapped[str] = mapped_column(String(100))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    disk_instance: Mapped['DiskInstance'] = relationship('DiskInstance', back_populates='requester_group_mount_rule')
    mount_policy: Mapped['MountPolicy'] = relationship('MountPolicy', back_populates='requester_group_mount_rule')


class RequesterMountRule(Base):
    __tablename__ = 'requester_mount_rule'
    __table_args__ = (
        ForeignKeyConstraint(['disk_instance_name'], ['disk_instance.disk_instance_name'], name='rqster_rule_din_fk'),
        ForeignKeyConstraint(['mount_policy_name'], ['mount_policy.mount_policy_name'], name='rqster_rule_mnt_plc_fk'),
        PrimaryKeyConstraint('disk_instance_name', 'requester_name', name='rqster_rule_pk'),
        Index('req_mnt_rule_din_idx', 'disk_instance_name'),
        Index('req_mnt_rule_mpn_idx', 'mount_policy_name')
    )

    disk_instance_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    requester_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    mount_policy_name: Mapped[str] = mapped_column(String(100))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    disk_instance: Mapped['DiskInstance'] = relationship('DiskInstance', back_populates='requester_mount_rule')
    mount_policy: Mapped['MountPolicy'] = relationship('MountPolicy', back_populates='requester_mount_rule')


class VirtualOrganization(Base):
    __tablename__ = 'virtual_organization'
    __table_args__ = (
        CheckConstraint("is_repack_vo = '1'::bpchar OR is_repack_vo IS NULL", name='virtual_organization_is_repack_vo_bool_ck'),
        ForeignKeyConstraint(['disk_instance_name'], ['disk_instance.disk_instance_name'], name='virtual_organization_din_fk'),
        PrimaryKeyConstraint('virtual_organization_id', name='virtual_organization_pk'),
        Index('virtual_org_din_idx', 'disk_instance_name'),
        Index('virtual_org_irvo_un_idx', 'is_repack_vo', unique=True),
        Index('virtual_org_von_ci_un_idx', unique=True),
        Index('virtual_org_von_un_idx', 'virtual_organization_name', unique=True)
    )

    virtual_organization_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    virtual_organization_name: Mapped[str] = mapped_column(String(100))
    read_max_drives: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    write_max_drives: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    max_file_size: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    disk_instance_name: Mapped[str] = mapped_column(String(100))
    is_repack_vo: Mapped[Optional[str]] = mapped_column(CHAR(1))

    disk_instance: Mapped['DiskInstance'] = relationship('DiskInstance', back_populates='virtual_organization')
    storage_class: Mapped[List['StorageClass']] = relationship('StorageClass', back_populates='virtual_organization')
    tape_pool: Mapped[List['TapePool']] = relationship('TapePool', back_populates='virtual_organization')


class DiskSystem(Base):
    __tablename__ = 'disk_system'
    __table_args__ = (
        ForeignKeyConstraint(['disk_instance_name', 'disk_instance_space_name'], ['disk_instance_space.disk_instance_name', 'disk_instance_space.disk_instance_space_name'], name='disk_system_din_disn_fk'),
        PrimaryKeyConstraint('disk_system_name', name='name_pk'),
        Index('disk_system_din_disn_idx', 'disk_instance_name', 'disk_instance_space_name'),
        Index('disk_system_dsn_ci_un_idx', unique=True)
    )

    disk_system_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    disk_instance_name: Mapped[str] = mapped_column(String(100))
    disk_instance_space_name: Mapped[str] = mapped_column(String(100))
    file_regexp: Mapped[str] = mapped_column(String(100))
    targeted_free_space: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    sleep_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    disk_instance_space: Mapped['DiskInstanceSpace'] = relationship('DiskInstanceSpace', back_populates='disk_system')


class StorageClass(Base):
    __tablename__ = 'storage_class'
    __table_args__ = (
        ForeignKeyConstraint(['virtual_organization_id'], ['virtual_organization.virtual_organization_id'], name='storage_class_voi_fk'),
        PrimaryKeyConstraint('storage_class_id', name='storage_class_pk'),
        Index('storage_class_scn_ci_un_idx', unique=True),
        Index('storage_class_scn_un_idx', 'storage_class_name', unique=True),
        Index('storage_class_voi_idx', 'virtual_organization_id')
    )

    storage_class_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    storage_class_name: Mapped[str] = mapped_column(String(100))
    nb_copies: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 0))
    virtual_organization_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    virtual_organization: Mapped['VirtualOrganization'] = relationship('VirtualOrganization', back_populates='storage_class')
    archive_file: Mapped[List['ArchiveFile']] = relationship('ArchiveFile', back_populates='storage_class')
    archive_route: Mapped[List['ArchiveRoute']] = relationship('ArchiveRoute', back_populates='storage_class')
    file_recycle_log: Mapped[List['FileRecycleLog']] = relationship('FileRecycleLog', back_populates='storage_class')


class TapePool(Base):
    __tablename__ = 'tape_pool'
    __table_args__ = (
        CheckConstraint("is_encrypted = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='tape_pool_is_encrypted_bool_ck'),
        ForeignKeyConstraint(['virtual_organization_id'], ['virtual_organization.virtual_organization_id'], name='tape_pool_vo_fk'),
        PrimaryKeyConstraint('tape_pool_id', name='tape_pool_pk'),
        Index('tape_pool_tpn_ci_un_idx', unique=True),
        Index('tape_pool_tpn_un_idx', 'tape_pool_name', unique=True),
        Index('tape_pool_voi_idx', 'virtual_organization_id')
    )

    tape_pool_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    tape_pool_name: Mapped[str] = mapped_column(String(100))
    virtual_organization_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    nb_partial_tapes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    is_encrypted: Mapped[str] = mapped_column(CHAR(1))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    encryption_key_name: Mapped[Optional[str]] = mapped_column(String(100))
    supply: Mapped[Optional[str]] = mapped_column(String(100))

    virtual_organization: Mapped['VirtualOrganization'] = relationship('VirtualOrganization', back_populates='tape_pool')
    supply_source_tape_pool: Mapped[List['TapePool']] = relationship('TapePool', secondary='tape_pool_supply', primaryjoin=lambda: TapePool.tape_pool_id == t_tape_pool_supply.c.supply_destination_tape_pool_id, secondaryjoin=lambda: TapePool.tape_pool_id == t_tape_pool_supply.c.supply_source_tape_pool_id, back_populates='supply_destination_tape_pool')
    supply_destination_tape_pool: Mapped[List['TapePool']] = relationship('TapePool', secondary='tape_pool_supply', primaryjoin=lambda: TapePool.tape_pool_id == t_tape_pool_supply.c.supply_source_tape_pool_id, secondaryjoin=lambda: TapePool.tape_pool_id == t_tape_pool_supply.c.supply_destination_tape_pool_id, back_populates='supply_source_tape_pool')
    archive_route: Mapped[List['ArchiveRoute']] = relationship('ArchiveRoute', back_populates='tape_pool')
    tape: Mapped[List['Tape']] = relationship('Tape', back_populates='tape_pool')


class ArchiveFile(Base):
    __tablename__ = 'archive_file'
    __table_args__ = (
        CheckConstraint("is_deleted = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='archive_file_id_bool_ck'),
        ForeignKeyConstraint(['disk_instance_name'], ['disk_instance.disk_instance_name'], name='archive_file_din_fk'),
        ForeignKeyConstraint(['storage_class_id'], ['storage_class.storage_class_id'], name='archive_file_storage_class_fk'),
        PrimaryKeyConstraint('archive_file_id', name='archive_file_pk'),
        UniqueConstraint('disk_instance_name', 'disk_file_id', name='archive_file_din_dfi_un'),
        Index('archive_file_dfi_idx', 'disk_file_id'),
        Index('archive_file_din_idx', 'disk_instance_name'),
        Index('archive_file_disk_file_uid_idx', 'archive_file_id', 'disk_file_uid'),
        Index('archive_file_sci_idx', 'storage_class_id')
    )

    archive_file_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    disk_instance_name: Mapped[str] = mapped_column(String(100))
    disk_file_id: Mapped[str] = mapped_column(String(100))
    disk_file_uid: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 0))
    disk_file_gid: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 0))
    size_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    checksum_adler32: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 0))
    storage_class_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    creation_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    reconciliation_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    is_deleted: Mapped[str] = mapped_column(CHAR(1), server_default=text("'0'::bpchar"))
    checksum_blob: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    collocation_hint: Mapped[Optional[str]] = mapped_column(String(100))

    disk_instance: Mapped['DiskInstance'] = relationship('DiskInstance', back_populates='archive_file')
    storage_class: Mapped['StorageClass'] = relationship('StorageClass', back_populates='archive_file')
    tape_file: Mapped[List['TapeFile']] = relationship('TapeFile', back_populates='archive_file')


class ArchiveRoute(Base):
    __tablename__ = 'archive_route'
    __table_args__ = (
        CheckConstraint("archive_route_type::text = ANY (ARRAY['DEFAULT'::character varying, 'REPACK'::character varying]::text[])", name='archive_route_art_string_ck'),
        CheckConstraint('copy_nb > 0::numeric', name='archive_route_copy_nb_gt_0_ck'),
        ForeignKeyConstraint(['storage_class_id'], ['storage_class.storage_class_id'], name='archive_route_storage_class_fk'),
        ForeignKeyConstraint(['tape_pool_id'], ['tape_pool.tape_pool_id'], name='archive_route_tape_pool_fk'),
        PrimaryKeyConstraint('storage_class_id', 'copy_nb', 'archive_route_type', name='archive_route_pk'),
        UniqueConstraint('storage_class_id', 'tape_pool_id', name='archive_route_sci_tpi_un')
    )

    storage_class_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    copy_nb: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 0), primary_key=True)
    tape_pool_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[str] = mapped_column(String(1000))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    archive_route_type: Mapped[str] = mapped_column(String(100), primary_key=True, server_default=text("'DEFAULT'::character varying"))

    storage_class: Mapped['StorageClass'] = relationship('StorageClass', back_populates='archive_route')
    tape_pool: Mapped['TapePool'] = relationship('TapePool', back_populates='archive_route')


class Tape(Base):
    __tablename__ = 'tape'
    __table_args__ = (
        CheckConstraint("dirty = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='tape_dirty_bool_ck'),
        CheckConstraint("is_from_castor = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='tape_is_from_castor_bool_ck'),
        CheckConstraint("is_full = ANY (ARRAY['0'::bpchar, '1'::bpchar])", name='tape_is_full_bool_ck'),
        CheckConstraint("tape_state::text = ANY (ARRAY['ACTIVE'::character varying, 'REPACKING_PENDING'::character varying, 'REPACKING'::character varying, 'REPACKING_DISABLED'::character varying, 'DISABLED'::character varying, 'BROKEN_PENDING'::character varying, 'BROKEN'::character varying, 'EXPORTED_PENDING'::character varying, 'EXPORTED'::character varying]::text[])", name='tape_state_ck'),
        CheckConstraint('vid::text = upper(vid::text)', name='tape_vid_ck'),
        ForeignKeyConstraint(['logical_library_id'], ['logical_library.logical_library_id'], name='tape_logical_library_fk'),
        ForeignKeyConstraint(['media_type_id'], ['media_type.media_type_id'], name='tape_media_type_fk'),
        ForeignKeyConstraint(['tape_pool_id'], ['tape_pool.tape_pool_id'], name='tape_tape_pool_fk'),
        PrimaryKeyConstraint('vid', name='tape_pk'),
        Index('tape_lli_idx', 'logical_library_id'),
        Index('tape_mti_idx', 'media_type_id'),
        Index('tape_state_idx', 'tape_state'),
        Index('tape_tape_pool_id_idx', 'tape_pool_id'),
        Index('tape_vid_ci_un_idx', unique=True)
    )

    vid: Mapped[str] = mapped_column(String(100), primary_key=True)
    media_type_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    vendor: Mapped[str] = mapped_column(String(100))
    logical_library_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    tape_pool_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    data_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_fseq: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    nb_master_files: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    master_data_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    is_full: Mapped[str] = mapped_column(CHAR(1))
    is_from_castor: Mapped[str] = mapped_column(CHAR(1))
    dirty: Mapped[str] = mapped_column(CHAR(1), server_default=text("'1'::bpchar"))
    nb_copy_nb_1: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    copy_nb_1_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    nb_copy_nb_gt_1: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    copy_nb_gt_1_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    read_mount_count: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    write_mount_count: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), server_default=text('0'))
    tape_state: Mapped[str] = mapped_column(String(100))
    state_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    state_modified_by: Mapped[str] = mapped_column(String(100))
    creation_log_user_name: Mapped[str] = mapped_column(String(100))
    creation_log_host_name: Mapped[str] = mapped_column(String(100))
    creation_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    last_update_user_name: Mapped[str] = mapped_column(String(100))
    last_update_host_name: Mapped[str] = mapped_column(String(100))
    last_update_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    purchase_order: Mapped[Optional[str]] = mapped_column(String(100))
    encryption_key_name: Mapped[Optional[str]] = mapped_column(String(100))
    label_format: Mapped[Optional[str]] = mapped_column(CHAR(1))
    label_drive: Mapped[Optional[str]] = mapped_column(String(100))
    label_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    last_read_drive: Mapped[Optional[str]] = mapped_column(String(100))
    last_read_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    last_write_drive: Mapped[Optional[str]] = mapped_column(String(100))
    last_write_time: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(20, 0))
    user_comment: Mapped[Optional[str]] = mapped_column(String(1000))
    state_reason: Mapped[Optional[str]] = mapped_column(String(1000))
    verification_status: Mapped[Optional[str]] = mapped_column(String(1000))

    logical_library: Mapped['LogicalLibrary'] = relationship('LogicalLibrary', back_populates='tape')
    media_type: Mapped['MediaType'] = relationship('MediaType', back_populates='tape')
    tape_pool: Mapped['TapePool'] = relationship('TapePool', back_populates='tape')
    file_recycle_log: Mapped[List['FileRecycleLog']] = relationship('FileRecycleLog', back_populates='tape')
    scanned_for_repack: Mapped[List['ScannedForRepack']] = relationship('ScannedForRepack', back_populates='tape')
    tape_file: Mapped[List['TapeFile']] = relationship('TapeFile', back_populates='tape')


t_tape_pool_supply = Table(
    'tape_pool_supply', Base.metadata,
    Column('supply_source_tape_pool_id', Numeric(20, 0), primary_key=True, nullable=False),
    Column('supply_destination_tape_pool_id', Numeric(20, 0), primary_key=True, nullable=False),
    CheckConstraint('supply_source_tape_pool_id <> supply_destination_tape_pool_id', name='no_self_supply_ck'),
    ForeignKeyConstraint(['supply_destination_tape_pool_id'], ['tape_pool.tape_pool_id'], ondelete='CASCADE', name='supply_destination_fk'),
    ForeignKeyConstraint(['supply_source_tape_pool_id'], ['tape_pool.tape_pool_id'], name='supply_source_fk'),
    PrimaryKeyConstraint('supply_source_tape_pool_id', 'supply_destination_tape_pool_id', name='supply_pk')
)


class FileRecycleLog(Base):
    __tablename__ = 'file_recycle_log'
    __table_args__ = (
        ForeignKeyConstraint(['storage_class_id'], ['storage_class.storage_class_id'], name='file_recycle_log_sc_fk'),
        ForeignKeyConstraint(['vid'], ['tape.vid'], name='file_recycle_log_vid_fk'),
        PrimaryKeyConstraint('file_recycle_log_id', name='file_recycle_log_pk'),
        Index('file_recycle_log_afi_idx', 'archive_file_id'),
        Index('file_recycle_log_dfi_idx', 'disk_file_id'),
        Index('file_recycle_log_din_idx', 'disk_instance_name'),
        Index('file_recycle_log_rlt_idx', 'recycle_log_time'),
        Index('file_recycle_log_scd_idx', 'storage_class_id'),
        Index('file_recycle_log_vid_idx', 'vid')
    )

    file_recycle_log_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    vid: Mapped[str] = mapped_column(String(100))
    fseq: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    block_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    copy_nb: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 0))
    tape_file_creation_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    archive_file_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    disk_instance_name: Mapped[str] = mapped_column(String(100))
    disk_file_id: Mapped[str] = mapped_column(String(100))
    disk_file_id_when_deleted: Mapped[str] = mapped_column(String(100))
    disk_file_uid: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    disk_file_gid: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    size_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    checksum_adler32: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 0))
    storage_class_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    archive_file_creation_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    reconciliation_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    reason_log: Mapped[str] = mapped_column(String(1000))
    recycle_log_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    checksum_blob: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    collocation_hint: Mapped[Optional[str]] = mapped_column(String(100))
    disk_file_path: Mapped[Optional[str]] = mapped_column(String(2000))

    storage_class: Mapped['StorageClass'] = relationship('StorageClass', back_populates='file_recycle_log')
    tape: Mapped['Tape'] = relationship('Tape', back_populates='file_recycle_log')


class ScannedForRepack(Base):
    __tablename__ = 'scanned_for_repack'
    __table_args__ = (
        ForeignKeyConstraint(['vid'], ['tape.vid'], ondelete='CASCADE', name='scanned_for_repack_vid_fkey'),
        PrimaryKeyConstraint('id', name='scanned_for_repack_pkey'),
        Index('idx_scanned_for_repack_vid', 'vid')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(20), server_default=text("'Marked for review'::character varying"))
    created: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    updated: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    vid: Mapped[Optional[str]] = mapped_column(String(100))

    tape: Mapped[Optional['Tape']] = relationship('Tape', back_populates='scanned_for_repack')


class TapeFile(Base):
    __tablename__ = 'tape_file'
    __table_args__ = (
        CheckConstraint('copy_nb > 0::numeric', name='tape_file_copy_nb_gt_0_ck'),
        ForeignKeyConstraint(['archive_file_id'], ['archive_file.archive_file_id'], name='tape_file_archive_file_fk'),
        ForeignKeyConstraint(['vid'], ['tape.vid'], name='tape_file_tape_fk'),
        PrimaryKeyConstraint('vid', 'fseq', name='tape_file_pk'),
        UniqueConstraint('vid', 'block_id', name='tape_file_vid_block_id_un'),
        Index('tape_file_archive_file_id_idx', 'archive_file_id'),
        Index('tape_file_vid_idx', 'vid')
    )

    vid: Mapped[str] = mapped_column(String(100), primary_key=True)
    fseq: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0), primary_key=True)
    block_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    logical_size_in_bytes: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    copy_nb: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 0))
    creation_time: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))
    archive_file_id: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 0))

    archive_file: Mapped['ArchiveFile'] = relationship('ArchiveFile', back_populates='tape_file')
    tape: Mapped['Tape'] = relationship('Tape', back_populates='tape_file')
