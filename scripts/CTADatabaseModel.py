#! /usr/bin/env python3


from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, Sequence, String, PrimaryKeyConstraint, CHAR
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


class Tape(Base):
    # FIXME: Vastly incomplete
    """
    CREATE TABLE TAPE(
      VID                     VARCHAR(100)    CONSTRAINT TAPE_V_NN    NOT NULL,
      MEDIA_TYPE_ID           NUMERIC(20, 0)      CONSTRAINT TAPE_MTID_NN NOT NULL,
      VENDOR                  VARCHAR(100)    CONSTRAINT TAPE_V2_NN   NOT NULL,
      LOGICAL_LIBRARY_ID      NUMERIC(20, 0)      CONSTRAINT TAPE_LLI_NN  NOT NULL,
      TAPE_POOL_ID            NUMERIC(20, 0)      CONSTRAINT TAPE_TPI_NN  NOT NULL,
      ENCRYPTION_KEY_NAME     VARCHAR(100),
      DATA_IN_BYTES           NUMERIC(20, 0)      CONSTRAINT TAPE_DIB_NN  NOT NULL,
      LAST_FSEQ               NUMERIC(20, 0)      CONSTRAINT TAPE_LF_NN   NOT NULL,
      NB_MASTER_FILES         NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_NB_MASTER_FILES_NN NOT NULL,
      MASTER_DATA_IN_BYTES    NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_MASTER_DATA_IN_BYTES_NN NOT NULL,
      IS_FULL                 CHAR(1)         CONSTRAINT TAPE_IF_NN   NOT NULL,
      IS_FROM_CASTOR          CHAR(1)         CONSTRAINT TAPE_IFC_NN  NOT NULL,
      DIRTY                   CHAR(1)         DEFAULT '1' CONSTRAINT TAPE_DIRTY_NN NOT NULL,
      NB_COPY_NB_1            NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_NB_COPY_NB_1_NN NOT NULL,
      COPY_NB_1_IN_BYTES      NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_COPY_NB_1_IN_BYTES_NN NOT NULL,
      NB_COPY_NB_GT_1         NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_NB_COPY_NB_GT_1_NN NOT NULL,
      COPY_NB_GT_1_IN_BYTES   NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_COPY_NB_GT_1_IN_BYTES_NN NOT NULL,
      LABEL_FORMAT            CHAR(1),
      LABEL_DRIVE             VARCHAR(100),
      LABEL_TIME              NUMERIC(20, 0),
      LAST_READ_DRIVE         VARCHAR(100),
      LAST_READ_TIME          NUMERIC(20, 0),
      LAST_WRITE_DRIVE        VARCHAR(100),
      LAST_WRITE_TIME         NUMERIC(20, 0),
      READ_MOUNT_COUNT        NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_RMC_NN NOT NULL,
      WRITE_MOUNT_COUNT       NUMERIC(20, 0)      DEFAULT 0 CONSTRAINT TAPE_WMC_NN NOT NULL,
      USER_COMMENT            VARCHAR(1000),
      TAPE_STATE              VARCHAR(100)    CONSTRAINT TAPE_TS_NN NOT NULL,
      STATE_REASON            VARCHAR(1000),
      STATE_UPDATE_TIME       NUMERIC(20, 0)      CONSTRAINT TAPE_SUT_NN NOT NULL,
      STATE_MODIFIED_BY       VARCHAR(100)    CONSTRAINT TAPE_SMB_NN NOT NULL,
      CREATION_LOG_USER_NAME  VARCHAR(100)    CONSTRAINT TAPE_CLUN_NN NOT NULL,
      CREATION_LOG_HOST_NAME  VARCHAR(100)    CONSTRAINT TAPE_CLHN_NN NOT NULL,
      CREATION_LOG_TIME       NUMERIC(20, 0)      CONSTRAINT TAPE_CLT_NN  NOT NULL,
      LAST_UPDATE_USER_NAME   VARCHAR(100)    CONSTRAINT TAPE_LUUN_NN NOT NULL,
      LAST_UPDATE_HOST_NAME   VARCHAR(100)    CONSTRAINT TAPE_LUHN_NN NOT NULL,
      LAST_UPDATE_TIME        NUMERIC(20, 0)      CONSTRAINT TAPE_LUT_NN  NOT NULL,
      VERIFICATION_STATUS     VARCHAR(1000),
      CONSTRAINT TAPE_PK PRIMARY KEY(VID),
      CONSTRAINT TAPE_LOGICAL_LIBRARY_FK FOREIGN KEY(LOGICAL_LIBRARY_ID) REFERENCES LOGICAL_LIBRARY(LOGICAL_LIBRARY_ID),
      CONSTRAINT TAPE_TAPE_POOL_FK FOREIGN KEY(TAPE_POOL_ID) REFERENCES TAPE_POOL(TAPE_POOL_ID),
      CONSTRAINT TAPE_IS_FULL_BOOL_CK CHECK(IS_FULL IN ('0', '1')),
      CONSTRAINT TAPE_IS_FROM_CASTOR_BOOL_CK CHECK(IS_FROM_CASTOR IN ('0', '1')),
      CONSTRAINT TAPE_DIRTY_BOOL_CK CHECK(DIRTY IN ('0','1')),
      CONSTRAINT TAPE_STATE_CK CHECK(TAPE_STATE IN ('ACTIVE', 'REPACKING', 'DISABLED', 'BROKEN')),
      CONSTRAINT TAPE_MEDIA_TYPE_FK FOREIGN KEY(MEDIA_TYPE_ID) REFERENCES MEDIA_TYPE(MEDIA_TYPE_ID)
    );
    """

    __tablename__ = 'tape'

    vid = Column(String)
    label_format = Column(CHAR(1))
    __table_args__ = (PrimaryKeyConstraint(vid), {},)
