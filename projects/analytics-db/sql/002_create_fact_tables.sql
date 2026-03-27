create table if not exists student_course_enrollments (
  enrollment_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  course_id text,
  course_code text,
  course_name text,
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_grade_records (
  grade_record_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  course_id text,
  course_name text,
  score numeric(6, 2),
  gpa numeric(4, 2),
  passed boolean,
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_attendance_records (
  attendance_record_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  attendance_status text,
  attended_at date,
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_signin_events (
  signin_event_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  signed_in_at timestamp,
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_assignment_submissions (
  assignment_submission_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  assignment_name text,
  submitted_at timestamp,
  submission_status text,
  score numeric(6, 2),
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_exam_submissions (
  exam_submission_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  exam_name text,
  submitted_at timestamp,
  score numeric(6, 2),
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_task_participation (
  task_participation_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  task_name text,
  participated_at timestamp,
  participation_status text,
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_discussion_events (
  discussion_event_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  discussion_topic text,
  replied_at timestamp,
  reply_count integer,
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_library_visits (
  library_visit_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  visited_at timestamp,
  visit_date date,
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_running_events (
  running_event_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  ran_at timestamp,
  run_date date,
  distance_km numeric(6, 2),
  source_file text not null,
  source_row_hash text not null
);

create table if not exists student_evaluation_labels (
  evaluation_label_id bigint generated always as identity primary key,
  student_id text not null,
  term_key text not null,
  risk_label text,
  evaluation_source text,
  source_file text not null,
  source_row_hash text not null
);
