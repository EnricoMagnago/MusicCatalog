#! /usr/bin/python3

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import exc, event, and_, or_
import datetime
import os
import glob
import shutil
from db.db_config import DB_CONFIG
from db.session_manager import Base, SessionManager


class MusicSheet(Base):
    """class that represent a music sheet in the ORM"""
    __tablename__ = "music_sheets"

    _id = Column('id', Integer, primary_key=True)
    _title = Column('title', String, nullable=False, unique=True, index=True)
    _files_path = Column('files_path', String, nullable=False, unique=True)
    _composer = Column('composer', String(50), nullable=True, index=True)
    _arranger = Column('arranger', String(50), nullable=True, index=True)
    _date_added = Column('date_added', Date, nullable=True, index=True)

    def __init__(self, title, composer=None, arranger=None):
        assert os.path.isdir(DB_CONFIG.music_sheets_base_path)

        self.title = title
        self.arranger = arranger
        self.composer = composer
        self.date_added = datetime.date.today()
        self.files_path = title.strip().lower().replace(' ', '_')

    def __repr__(self):
        res = "<MusicSheet "
        obj_id = self.id
        title = self.title
        composer = self.composer
        arranger = self.arranger
        date_added = self.date_added
        files_path = self.files_path
        if obj_id is not None:
            res += f"id={obj_id} "
        if title is not None:
            res += f"title='{title}' "
        if composer is not None:
            res += f"composer='{composer}' "
        if arranger is not None:
            res += f"arranger='{arranger}' "
        if date_added is not None:
            res += f"date_added='{date_added}' "
        if files_path is not None:
            res += f"base_path='{files_path}' "
        res += "></MusicSheet>"
        return res

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def composer(self):
        return self._composer

    @property
    def arranger(self):
        return self._arranger

    @property
    def date_added(self):
        return self._date_added

    @property
    def files_path(self):
        return os.path.join(DB_CONFIG.music_sheets_base_path, self._files_path)

    @title.setter
    def title(self, title):
        self._title = title

    @composer.setter
    def composer(self, composer):
        self._composer = composer

    @arranger.setter
    def arranger(self, arranger):
        self._arranger = arranger

    @date_added.setter
    def date_added(self, date_added):
        self._date_added = date_added

    @files_path.setter
    def files_path(self, files_path):
        self._files_path = files_path

    def add_instrument_sheet(self, instrument_name, number, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} does not exist")
        base_dir = self.files_path
        instrument_name = instrument_name.strip().lower().replace(' ', '_')
        instrument_dir = os.path.join(base_dir, instrument_name)
        if not os.path.isdir(instrument_dir):
            os.mkdir(instrument_dir)
        _, extension = os.path.splitext(file_path)
        dst_file = self.title.strip().lower().replace(' ', '_')
        dst_file += f"_{instrument_name}_{number}{extension}"
        dst_file = os.path.join(instrument_dir, dst_file)
        if os.path.exists(dst_file):
            raise FileExistsError(f"{dst_file} already exists")
        shutil.copy2(file_path, dst_file)

    def remove_instrument_sheet(self, instrument_name, number):
        retval = False
        base_dir = self.files_path
        instrument_name = instrument_name.strip().lower().replace(' ', '_')
        instrument_dir = os.path.join(base_dir, instrument_name)
        if os.path.isdir(instrument_dir):
            dst_files = self.title.strip().lower().replace(' ', '_')
            dst_files += f"_{instrument_name}_{number}*"
            dst_files = os.path.join(instrument_dir, dst_files)
            for dst_file in glob.glob(dst_files):
                os.remove(dst_file)
                retval = True
        return retval

    @property
    def instruments(self):
        base_dir = self.files_path
        return [name for name in os.listdir(base_dir)
                if os.path.isdir(os.path.join(base_dir, name))]

    def numbers_for_instrument(self, instrument_name):
        retval = []
        base_dir = self.files_path
        instrument_name = instrument_name.strip().lower().replace(' ', '_')
        instrument_dir = os.path.join(base_dir, instrument_name)
        if not os.path.isdir(instrument_dir):
            raise FileNotFoundError(f"{instrument_dir} does not exist")
        for file_name in os.listdir(instrument_dir):
            if os.path.isfile(os.path.join(instrument_dir, file_name)):
                name, _ = os.path.splitext(file_name)
                pos = name.rfind('_')
                try:
                    num = int(name[pos + 1:])
                except ValueError:
                    raise ImportWarning("Malformed file name: {file_name}")
                retval.append(num)
        return retval

    def _insert_call_back(mapper, connection, target):
        files_dir = target.files_path
        assert not os.path.exists(files_dir)
        os.mkdir(files_dir)

    def _delete_call_back(mapper, connection, target):
        target.delete()

    def delete(self):
        files_dir = self.files_path
        if os.path.isdir(files_dir):
            shutil.rmtree(os.path.abspath(files_dir))


# add annotation to callbacks, can not access MusicSheet from within
MusicSheet._delete_call_back = \
        event.listens_for(MusicSheet, 'before_delete') \
        (MusicSheet._delete_call_back)

MusicSheet._insert_call_back = \
        event.listens_for(MusicSheet, 'after_insert') \
        (MusicSheet._insert_call_back)


class MusicSheetMgr(object):
    """Encapsulate queries"""

    def find_id(session, id):
        return session.query(MusicSheet).get(id)

    def add(session, sheet):
        session.add(sheet)

    def del_sheet(session, sheet):
        session.delete(sheet)

    def del_id(session, id):
        sheet = MusicSheetMgr.find_id(session, id)
        MusicSheetMgr.del_sheet(sheet)

    def search(session, title=None, composer=None, arranger=None,
               date_added_min=None, date_added_max=None,
               sort_asc_title=True, conjunct=True):
        query = session.query(MusicSheet)
        query_filter = []

        if title is not None:
            title = title.strip()
            query_filter.append(MusicSheet._title.ilike(f'%{title}%'))
        if composer is not None:
            composer = composer.strip()
            query_filter.append(MusicSheet._composer.ilike(f'%{composer}%'))
        if arranger is not None:
            arranger = arranger.strip()
            query_filter.append(MusicSheet._arranger.ilike(f'%{arranger}%'))
        if date_added_min is not None:
            query_filter.append(MusicSheet._date_added >= date_added_min)

        if len(query_filter) > 0:
            if conjunct:
                query = query.filter(and_(*query_filter))
            else:
                query = query.filter(or_(*query_filter))
        if sort_asc_title:
            query = query.order_by(MusicSheet._title)
        return query.all()

    def check_consistency(session):
        inconsistencies_missing_in_fs = []
        inconsistencies_missing_in_db = []
        base_dir = DB_CONFIG.music_sheets_base_path
        # get all sheets in db.
        db_sheets = MusicSheetMgr.search(session, sort_asc_title=False)
        # get all sheets from file system.
        fs_sheets = set()
        for f in os.listdir(base_dir):
            f_abs = os.path.join(base_dir, f)
            if os.path.isdir(f_abs):
                fs_sheets.add(f_abs)

        # collect set of paths in db
        paths_in_db = set()
        for db_sheet in db_sheets:
            paths_in_db.add(db_sheet.files_path)
            if db_sheet.files_path not in fs_sheets:
                assert not os.path.isdir(os.path.join(base_dir,
                                                      db_sheet.files_path)), \
                        f"{db_sheet}\n{fs_sheets}"
                inconsistencies_missing_in_fs.append(db_sheet)

        inconsistencies_missing_in_db = \
            [fs for fs in fs_sheets if fs not in paths_in_db]

        return inconsistencies_missing_in_fs, inconsistencies_missing_in_db


def main(argv):
    def user_interaction_add_music_sheet(session_mgr):
        title = None
        while not title:
            title = input("Insert title: ").strip()
        composer = input("Insert composer (can be empty): ").strip()
        arranger = input("Insert arranger (can be empty): ").strip()
        sheet = MusicSheet(title=title, composer=composer,
                           arranger=arranger)
        with session_mgr as session:
            try:
                MusicSheetMgr.add(session, sheet)
                session.commit()
            except exc.SQLAlchemyError as e:
                session.rollback()
                print(f"ERROR: could not add, exception: {e}")

    def user_interaction_search_music_sheet(session_mgr):
        ret_sheet = None
        date_format = "%d-%m-%Y"
        title = None
        composer = None
        arranger = None
        date_added_min = None
        date_added_max = None
        title = input("Insert title (can be empty): ").strip()
        if not title:
            title = None
        composer = input("Insert composer (can be empty): ").strip()
        if not composer:
            composer = None
        arranger = input("Insert arranger (can be empty): ").strip()
        if not arranger:
            arranger = None
        correct = False
        while not correct:
            correct = True
            date_added_min = input("Insert min date (can be empty), "
                                   f"format {date_format}: ").strip()
            if not date_added_min:
                date_added_min = None
            else:
                try:
                    date_added_min = datetime.datetime.strptime(date_added_min,
                                                                date_format)
                except ValueError as e:
                    print(f"Exception: {e}")
                    correct = False
        correct = False
        while not correct:
            correct = True
            date_added_max = input("Insert max date (can be empty), "
                                   f"format {date_format}: ").strip()
            if not date_added_max:
                date_added_max = None
            else:
                try:
                    date_added_max = datetime.datetime.strptime(date_added_max,
                                                                date_format)
                except ValueError as e:
                    print(f"Exception: {e}")
                    correct = False
        with session_mgr as session:
            music_sheets = \
                MusicSheetMgr.search(session, title=title, composer=composer,
                                     arranger=arranger,
                                     date_added_min=date_added_min,
                                     date_added_max=date_added_max)
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
        if len(music_sheets) == 0:
            print("Empty")
        for (i, sheet) in enumerate(music_sheets):
            print(f"{i}) {sheet}")
        print("\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
        if len(music_sheets):
            correct = False
            while not correct:
                correct = True
                sheet_id = input("Select sheet id: "
                                 f"[0, {len(music_sheets) - 1}], "
                                 "-1 to avoid selection: ")
                try:
                    sheet_id = int(sheet_id)
                    if sheet_id >= 0 and sheet_id < len(music_sheets):
                        ret_sheet = music_sheets[sheet_id]
                    elif sheet_id != -1:
                        raise ValueError(f"Out of bounds: {sheet_id}")
                except ValueError:
                    correct = False
        return ret_sheet

    def user_interaction_add_instrument(session_manager, selected_sheet):
        curr_instruments = sorted(selected_sheet.instruments)
        print("\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        print("Current instruments:")
        for instrument in curr_instruments:
            print(f"\t{instrument}")
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
        instrument = input("Insert instrument name: ").strip()
        if instrument in curr_instruments:
            numbers = \
              sorted(selected_sheet.numbers_for_instrument(instrument))
            print("\n- - - - - - - - - - - - - "
                  "- - - - - - - - - - - - - - - -")
            print(f"Current numbers for {instrument}:", end="")
            for num in numbers:
                print(f" {num}", end="")
            print("\n- - - - - - - - - - - - - "
                  "- - - - - - - - - - - - - - - -")
        correct = False
        while not correct:
            correct = True
            instr_num = input("Instrument number (> 0): ").strip()
            try:
                instr_num = int(instr_num)
                if instr_num <= 0:
                    correct = False
            except ValueError:
                correct = False
        correct = False
        while not correct:
            correct = True
            file_path = input("File path: ").strip()
            if not file_path:
                correct = False
            else:
                if not file_path.startswith('/'):
                    cwd = os.getcwd()
                    file_path = os.path.join(cwd, file_path)
                file_path = os.path.abspath(file_path)
                if not os.path.isfile(file_path):
                    print(f"Can not find file: '{file_path}'")
                    correct = False
                elif not os.access(file_path, os.R_OK):
                    print(f"Can not read file: '{file_path}'")
                    correct = False
        try:
            selected_sheet.add_instrument_sheet(instrument, instr_num,
                                                file_path)
        except FileExistsError:
            print("File already exists, can not overwrite it")

    def user_interaction_delete_instrument(session_mgr, selected_sheet):
        instrument = None
        curr_instruments = sorted(selected_sheet.instruments)
        while instrument not in curr_instruments:
            print("\n- - - - - - - - - - - - - - - - - - - - - - - - - - - -")
            print("Current instruments:")
            for instrument in curr_instruments:
                print(f"\t{instrument}")
            print("- - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
            instrument = input("Insert instrument name: ").strip()
        instr_num = None
        curr_nums = \
            sorted(selected_sheet.numbers_for_instrument(instrument))
        while instr_num not in curr_nums:
            print("\n- - - - - - - - - - - - - "
                  "- - - - - - - - - - - - - - - -")
            print(f"Current numbers for {instrument}:", end="")
            for num in curr_nums:
                print(f" {num}", end="")
            print("\n- - - - - - - - - - - - - "
                  "- - - - - - - - - - - - - - - -")
            instr_num = input("Instrument number (> 0): ").strip()
            try:
                instr_num = int(instr_num)
            except ValueError:
                instr_num = None
        deleted = selected_sheet.remove_instrument_sheet(instrument, instr_num)
        if not deleted:
            print("Could not delete file")

    def user_interaction_delete_sheet(session_mgr, sheet):
        with session_mgr as session:
            try:
                MusicSheetMgr.del_sheet(session, sheet)
                session.commit()
            except exc.SQLAlchemyError as e:
                    session.rollback()
                    print(f"ERROR: could not remove, exception: {e}")

    def self_check(session_mgr):
        missing_in_fs = []
        missing_in_db = []
        with session_mgr as session:
            missing_in_fs, missing_in_db = \
                            MusicSheetMgr.check_consistency(session)
        if len(missing_in_fs) == 0 and len(missing_in_db) == 0:
            print("OK")
        if len(missing_in_fs) > 0:
            print(f"{len(missing_in_fs)} objects missing in file system:")
            for i, item in enumerate(missing_in_fs):
                print(f"\t{i}) {item}")
        if len(missing_in_db) > 0:
            print(f"\n{len(missing_in_db)} paths missing in database records:")
            for i, item in enumerate(missing_in_db):
                print(f"\t{i}) {item}")

    session_mgr = SessionManager()
    selected_sheet = None
    user_input = '-'
    while user_input != '0':
        user_input = \
            input("\n\n<-> <-> <-> <-> <-> <-> <-> <-> <-> <-> <-> <-> <->\n"
                  "Select action:\n"
                  "\t0 'exit'\t\t: close program\n"
                  "\t1 'add music sheet'\t: insert new music sheet\n"
                  "\t2 'search music sheet'\t: search music sheet in db\n"
                  "\t3 'show selected'\t: print selected music sheet\n"
                  "\t4 'add instrument'\t: add instrument sheet to selected\n"
                  "\t5 'del instrument'\t: del instrum sheet from selected\n"
                  "\t6 'delete selected'\t: delete selected music sheet\n"
                  "\t7 'self check'\t\t: check db-fs consistency, "
                  "if someone is writing data the result might be WRONG\n"
                  "\n<-> <-> <-> <-> <-> <-> <-> <-> <-> <-> <-> <-> <->\n")
        user_input = user_input.strip().lower()
        if user_input in ['0', 'exit']:
            user_input = '0'
        elif user_input in ['1', 'add music sheet']:
            user_interaction_add_music_sheet(session_mgr)
        elif user_input in ['2', 'search music sheet']:
            selected_sheet = user_interaction_search_music_sheet(session_mgr)
        elif user_input in ['3', 'show selected']:
            print(f"selected sheet:\n{selected_sheet}")
        elif user_input in ['4', 'add instrument']:
            if selected_sheet:
                user_interaction_add_instrument(session_mgr,
                                                selected_sheet)
            else:
                print("A sheet has to be selected first")
        elif user_input in ['5', 'del instrument']:
            user_interaction_delete_instrument(session_mgr,
                                               selected_sheet)
        elif user_input in ['6', 'delete selected']:
            if selected_sheet:
                user_interaction_delete_sheet(session_mgr, selected_sheet)
                selected_sheet = None
            else:
                print("Please select the sheet to be deleted")
        elif user_input in ['7', 'self check']:
            self_check(session_mgr)


if __name__ == "__main__":
    import sys
    main(sys.argv)
