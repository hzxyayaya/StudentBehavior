create table if not exists runtime_student_term_features (
  student_id text not null,
  term_key text not null,
  payload_json text not null,
  primary key (student_id, term_key)
);

create table if not exists runtime_student_results (
  student_id text not null,
  term_key text not null,
  payload_json text not null,
  primary key (student_id, term_key)
);

create table if not exists runtime_student_reports (
  student_id text not null,
  term_key text not null,
  payload_json text not null,
  primary key (student_id, term_key)
);

create table if not exists runtime_model_summary (
  summary_key text primary key,
  payload_json text not null
);

create table if not exists runtime_overview (
  summary_key text primary key,
  payload_json text not null
);

create table if not exists runtime_warnings (
  summary_key text primary key,
  payload_json text not null
);
