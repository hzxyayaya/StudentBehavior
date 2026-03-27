create index if not exists idx_student_course_enrollments_student_term
  on student_course_enrollments (student_id, term_key);

create index if not exists idx_student_grade_records_student_term
  on student_grade_records (student_id, term_key);

create index if not exists idx_student_attendance_records_student_term
  on student_attendance_records (student_id, term_key);

create index if not exists idx_student_signin_events_student_term
  on student_signin_events (student_id, term_key);

create index if not exists idx_student_assignment_submissions_student_term
  on student_assignment_submissions (student_id, term_key);

create index if not exists idx_student_exam_submissions_student_term
  on student_exam_submissions (student_id, term_key);

create index if not exists idx_student_task_participation_student_term
  on student_task_participation (student_id, term_key);

create index if not exists idx_student_discussion_events_student_term
  on student_discussion_events (student_id, term_key);

create index if not exists idx_student_library_visits_student_term
  on student_library_visits (student_id, term_key);

create index if not exists idx_student_running_events_student_term
  on student_running_events (student_id, term_key);

create index if not exists idx_student_evaluation_labels_student_term
  on student_evaluation_labels (student_id, term_key);
