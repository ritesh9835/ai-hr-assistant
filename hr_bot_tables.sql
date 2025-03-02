CREATE TABLE IF NOT EXISTS public.assessments
(
    id integer NOT NULL DEFAULT nextval('assessments_id_seq'::regclass),
    candidate_id integer,
    score integer,
    summary text COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT assessments_pkey PRIMARY KEY (id),
    CONSTRAINT assessments_candidate_id_fkey FOREIGN KEY (candidate_id)
        REFERENCES public.candidates (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT assessments_score_check CHECK (score >= 0 AND score <= 100)
)



CREATE TABLE IF NOT EXISTS public.candidates
(
    id integer NOT NULL DEFAULT nextval('candidates_id_seq'::regclass),
    email character varying(255) COLLATE pg_catalog."default" NOT NULL,
    resume_path text COLLATE pg_catalog."default" NOT NULL,
    job_url text COLLATE pg_catalog."default" NOT NULL,
    summary text COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT candidates_pkey PRIMARY KEY (id),
    CONSTRAINT candidates_email_key UNIQUE (email)
)



CREATE TABLE IF NOT EXISTS public.screening_questions
(
    id integer NOT NULL DEFAULT nextval('screening_questions_id_seq'::regclass),
    job_url text COLLATE pg_catalog."default" NOT NULL,
    question text COLLATE pg_catalog."default" NOT NULL,
    question_type character varying(50) COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT screening_questions_pkey PRIMARY KEY (id),
    CONSTRAINT screening_questions_question_type_check CHECK (question_type::text = ANY (ARRAY['subjective'::character varying, 'coding'::character varying]::text[]))
)