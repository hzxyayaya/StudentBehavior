create table if not exists students (
  student_id text primary key,
  gender text,
  ethnicity text,
  political_status text,
  major_name text,
  college_name text,
  class_name text,
  enrollment_year integer
);

create table if not exists terms (
  term_key text primary key,
  school_year text not null,
  term_no integer not null,
  term_name text not null,
  start_date date,
  end_date date,
  is_analysis_term boolean not null default true
);

create table if not exists courses (
  course_id text primary key,
  course_code text,
  course_name text not null,
  course_type text,
  credit numeric(6, 2),
  hours integer,
  assessment_type text
);

create table if not exists majors (
  major_id text primary key,
  major_name text not null,
  college_name text
);
