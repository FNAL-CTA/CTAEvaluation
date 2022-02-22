#! /usr/bin/env python3


from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, Sequence, String, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, relationship

# declarative base class
Base = declarative_base()


# an example mapping using the base
class ArchiveFile(Base):
    """
    CREATE TABLE public.archive_file (
        archive_file_id numeric(20,0) NOT NULL,
        disk_instance_name character varying(100) NOT NULL,
        disk_file_id character varying(100) NOT NULL,
        disk_file_uid numeric(10,0) NOT NULL,
        disk_file_gid numeric(10,0) NOT NULL,
        size_in_bytes numeric(20,0) NOT NULL,
        checksum_blob bytea,
        checksum_adler32 numeric(10,0) NOT NULL,
        storage_class_id numeric(20,0) NOT NULL,
        creation_time numeric(20,0) NOT NULL,
        reconciliation_time numeric(20,0) NOT NULL,
        is_deleted character(1) DEFAULT '0'::bpchar NOT NULL,
        collocation_hint character varying(100),
        CONSTRAINT archive_file_id_bool_ck CHECK ((is_deleted = ANY (ARRAY['0'::bpchar, '1'::bpchar])))
    );
    """
    __tablename__ = 'archive_file'

    archive_file_id = Column(Integer, Sequence('archive_file_id_seq'), primary_key=True)
    disk_instance_name = Column(String)
    disk_file_id = Column(String)
    disk_file_uid = Column(Integer)
    disk_file_gid = Column(Integer)
    size_in_bytes = Column(Integer)
    checksum_blob = Column(LargeBinary)
    checksum_adler32 = Column(Integer)
    storage_class_id = Column(Integer)
    creation_time = Column(Integer)
    reconciliation_time = Column(Integer)
    is_deleted = Column(String)
    collocation_hint = Column(String)

    tape_files = relationship("TapeFile", back_populates="archive_file")

    def __repr__(self) -> str:
        return (f"<ArchiveFile(archive_file_id='{self.archive_file_id}', disk_file_id='{self.disk_file_id}', "
                + f"size_in_bytes='{self.size_in_bytes}', checksum_adler32='{self.checksum_adler32}')>")


class TapeFile(Base):
    """
    CREATE TABLE public.tape_file (
        vid character varying(100) NOT NULL,
        fseq numeric(20,0) NOT NULL,
        block_id numeric(20,0) NOT NULL,
        logical_size_in_bytes numeric(20,0) NOT NULL,
        copy_nb numeric(3,0) NOT NULL,
        creation_time numeric(20,0) NOT NULL,
        archive_file_id numeric(20,0) NOT NULL,
        CONSTRAINT tape_file_copy_nb_gt_0_ck CHECK ((copy_nb > (0)::numeric))
    );
    """
    __tablename__ = 'tape_file'

    vid = Column(String)
    fseq = Column(Integer)
    block_id = Column(Integer)
    logical_size_in_bytes = Column(Integer)
    copy_nb = Column(Integer)
    creation_time = Column(Integer)
    archive_file_id = Column(Integer, ForeignKey('archive_file.archive_file_id'))

    archive_file = relationship("ArchiveFile", back_populates="tape_files")
    __table_args__ = (PrimaryKeyConstraint(vid, fseq), {},)

    def __repr__(self) -> str:
        return (f"<TapeFile(vid='{self.vid}', fseq='{self.fseq}', "
                + f"logical_size_in_bytes='{self.logical_size_in_bytes}', archive_file_id='{self.archive_file_id}')>")
