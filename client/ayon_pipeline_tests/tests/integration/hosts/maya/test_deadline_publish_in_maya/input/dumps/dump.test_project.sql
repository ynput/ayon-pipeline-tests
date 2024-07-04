DROP SCHEMA IF EXISTS project_test_project CASCADE;
DELETE FROM public.projects WHERE name = 'test_project';

INSERT INTO public.projects (name, code, library, config, attrib, data, active, created_at, updated_at) VALUES 
('test_project', 'tp', false, '{"roots": {"work": {"linux": "/mnt/share/projects", "darwin": "/Volumes/projects", 
"windows": "C:/projects"}}, "templates": {"hero": {"default": {"file": 
"{project[code]}_{folder[name]}_{task[name]}_hero<_{comment}>.{ext}", "directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/publish/{product[type]}/{product[name]}/hero"}}, "work": 
{"unreal": {"file": "{project[code]}_{folder[name]}.{ext}", "directory": 
"{root[work]}/{project[name]}/unreal/{task[name]}"}, "default": {"file": 
"{project[code]}_{folder[name]}_{task[name]}_{@version}<_{comment}>.{ext}", "directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/work/{task[name]}"}}, "common": {"frame": 
"{frame:0>{@frame_padding}}", "version": "v{version:0>{@version_padding}}", "frame_padding": 4, "version_padding": 3}, 
"publish": {"online": {"file": "{originalBasename}<.{@frame}><_{udim}>.{ext}", "directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/publish/{product[type]}/{product[name]}/{@version}"}, 
"render": {"file": "{project[code]}_{folder[name]}_{product[name]}_{@version}<_{output}><.{@frame}>.{ext}", 
"directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/publish/{product[type]}/{product[name]}/{@version}"}, 
"source": {"file": "{originalBasename}.{ext}", "directory": "{root[work]}/{originalDirname}"}, "default": {"file": 
"{project[code]}_{folder[name]}_{product[name]}_{@version}<_{output}><.{@frame}><_{udim}>.{ext}", "directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/publish/{product[type]}/{product[name]}/{@version}"}, 
"maya2unreal": {"file": "{product[name]}_{@version}<_{output}><.{@frame}>.{ext}", "directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/publish/{product[type]}"}, "simpleUnrealTexture": {"file": 
"{originalBasename}_{@version}.{ext}", "directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/publish/{product[type]}/{@version}"}, 
"simpleUnrealTextureHero": {"file": "{originalBasename}.{ext}", "directory": 
"{root[work]}/{project[name]}/{hierarchy}/{folder[name]}/publish/{product[type]}/hero"}}}}', '{"fps": 25.0, "tools": 
[], "clipIn": 1, "clipOut": 1, "frameEnd": 1010, "handleEnd": 0, "frameStart": 1001, "handleStart": 0, "pixelAspect": 
1.0, "applications": ["nuke/15-0", "nuke/13-0", "nuke/14-0", "nuke/13-2"], "resolutionWidth": 1920, 
"resolutionHeight": 1080}', '{}', true, '2024-05-20 16:34:36.764021+00', '2024-05-22 12:01:15.164895+00');


--
-- PostgreSQL database dump
--

-- Dumped from database version 15.7 (Debian 15.7-1.pgdg120+1)
-- Dumped by pg_dump version 15.7 (Debian 15.7-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: project_test_project; Type: SCHEMA; Schema: -; Owner: ayon
--

CREATE SCHEMA project_test_project;


ALTER SCHEMA project_test_project OWNER TO ayon;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: access_groups; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.access_groups (
    name character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.access_groups OWNER TO ayon;

--
-- Name: activities; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.activities (
    id uuid NOT NULL,
    activity_type character varying NOT NULL,
    body text NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.activities OWNER TO ayon;

--
-- Name: activities_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.activities_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.activities_creation_order_seq OWNER TO ayon;

--
-- Name: activities_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.activities_creation_order_seq OWNED BY project_test_project.activities.creation_order;


--
-- Name: activity_references; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.activity_references (
    id uuid NOT NULL,
    activity_id uuid NOT NULL,
    reference_type character varying NOT NULL,
    entity_type character varying NOT NULL,
    entity_id uuid,
    entity_name character varying,
    active boolean DEFAULT true NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.activity_references OWNER TO ayon;

--
-- Name: entity_paths; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.entity_paths (
    entity_id uuid NOT NULL,
    entity_type character varying NOT NULL,
    path character varying NOT NULL
);


ALTER TABLE project_test_project.entity_paths OWNER TO ayon;

--
-- Name: activity_feed; Type: VIEW; Schema: project_test_project; Owner: ayon
--

CREATE VIEW project_test_project.activity_feed AS
 SELECT ref.id AS reference_id,
    ref.activity_id,
    ref.reference_type,
    ref.entity_type,
    ref.entity_id,
    ref.entity_name,
    ref_paths.path AS entity_path,
    ref.created_at,
    ref.updated_at,
    ref.creation_order,
    act.activity_type,
    act.body,
    act.data AS activity_data,
    ref.data AS reference_data,
    ref.active
   FROM ((project_test_project.activity_references ref
     JOIN project_test_project.activities act ON ((ref.activity_id = act.id)))
     LEFT JOIN project_test_project.entity_paths ref_paths ON ((ref.entity_id = ref_paths.entity_id)));


ALTER TABLE project_test_project.activity_feed OWNER TO ayon;

--
-- Name: activity_references_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.activity_references_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.activity_references_creation_order_seq OWNER TO ayon;

--
-- Name: activity_references_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.activity_references_creation_order_seq OWNED BY project_test_project.activity_references.creation_order;


--
-- Name: addon_data; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.addon_data (
    addon_name character varying NOT NULL,
    addon_version character varying NOT NULL,
    key character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.addon_data OWNER TO ayon;

--
-- Name: custom_roots; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.custom_roots (
    site_id character varying NOT NULL,
    user_name character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.custom_roots OWNER TO ayon;

--
-- Name: exported_attributes; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.exported_attributes (
    folder_id uuid NOT NULL,
    path character varying NOT NULL,
    attrib jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.exported_attributes OWNER TO ayon;

--
-- Name: files; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.files (
    id uuid NOT NULL,
    size bigint NOT NULL,
    author character varying,
    activity_id uuid,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE project_test_project.files OWNER TO ayon;

--
-- Name: folder_types; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.folder_types (
    name character varying NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.folder_types OWNER TO ayon;

--
-- Name: folders; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.folders (
    id uuid NOT NULL,
    name character varying NOT NULL,
    label character varying,
    folder_type character varying NOT NULL,
    parent_id uuid,
    thumbnail_id uuid,
    attrib jsonb DEFAULT '{}'::jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    status character varying NOT NULL,
    tags character varying[] DEFAULT ARRAY[]::character varying[] NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.folders OWNER TO ayon;

--
-- Name: folders_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.folders_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.folders_creation_order_seq OWNER TO ayon;

--
-- Name: folders_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.folders_creation_order_seq OWNED BY project_test_project.folders.creation_order;


--
-- Name: hierarchy; Type: MATERIALIZED VIEW; Schema: project_test_project; Owner: ayon
--

CREATE MATERIALIZED VIEW project_test_project.hierarchy AS
 WITH htable AS (
         WITH RECURSIVE hierarchy AS (
                 SELECT folders.id,
                    folders.name,
                    folders.parent_id,
                    1 AS pos,
                    folders.id AS base_id
                   FROM project_test_project.folders
                UNION
                 SELECT e.id,
                    e.name,
                    e.parent_id,
                    (s.pos + 1),
                    s.base_id
                   FROM (project_test_project.folders e
                     JOIN hierarchy s ON ((s.parent_id = e.id)))
                )
         SELECT hierarchy.base_id,
            string_agg((hierarchy.name)::text, '/'::text ORDER BY hierarchy.pos DESC) AS path
           FROM hierarchy
          GROUP BY hierarchy.base_id
        )
 SELECT htable.base_id AS id,
    htable.path
   FROM htable
  WITH NO DATA;


ALTER TABLE project_test_project.hierarchy OWNER TO ayon;

--
-- Name: link_types; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.link_types (
    name character varying NOT NULL,
    input_type character varying NOT NULL,
    output_type character varying NOT NULL,
    link_type character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.link_types OWNER TO ayon;

--
-- Name: links; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.links (
    id uuid NOT NULL,
    name character varying,
    link_type character varying NOT NULL,
    input_id uuid NOT NULL,
    output_id uuid NOT NULL,
    author character varying,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.links OWNER TO ayon;

--
-- Name: links_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.links_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.links_creation_order_seq OWNER TO ayon;

--
-- Name: links_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.links_creation_order_seq OWNED BY project_test_project.links.creation_order;


--
-- Name: products; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.products (
    id uuid NOT NULL,
    name character varying NOT NULL,
    folder_id uuid NOT NULL,
    product_type character varying NOT NULL,
    attrib jsonb DEFAULT '{}'::jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    active boolean DEFAULT true NOT NULL,
    status character varying NOT NULL,
    tags character varying[] DEFAULT ARRAY[]::character varying[] NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.products OWNER TO ayon;

--
-- Name: products_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.products_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.products_creation_order_seq OWNER TO ayon;

--
-- Name: products_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.products_creation_order_seq OWNED BY project_test_project.products.creation_order;


--
-- Name: project_site_settings; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.project_site_settings (
    addon_name character varying NOT NULL,
    addon_version character varying NOT NULL,
    site_id character varying NOT NULL,
    user_name character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.project_site_settings OWNER TO ayon;

--
-- Name: representations; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.representations (
    id uuid NOT NULL,
    name character varying NOT NULL,
    version_id uuid NOT NULL,
    files jsonb DEFAULT '[]'::jsonb NOT NULL,
    attrib jsonb DEFAULT '{}'::jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    active boolean DEFAULT true NOT NULL,
    status character varying NOT NULL,
    tags character varying[] DEFAULT ARRAY[]::character varying[] NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.representations OWNER TO ayon;

--
-- Name: representations_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.representations_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.representations_creation_order_seq OWNER TO ayon;

--
-- Name: representations_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.representations_creation_order_seq OWNED BY project_test_project.representations.creation_order;


--
-- Name: settings; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.settings (
    addon_name character varying NOT NULL,
    addon_version character varying NOT NULL,
    variant character varying DEFAULT 'production'::character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.settings OWNER TO ayon;

--
-- Name: statuses; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.statuses (
    name character varying NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.statuses OWNER TO ayon;

--
-- Name: tags; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.tags (
    name character varying NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.tags OWNER TO ayon;

--
-- Name: task_types; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.task_types (
    name character varying NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE project_test_project.task_types OWNER TO ayon;

--
-- Name: tasks; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.tasks (
    id uuid NOT NULL,
    name character varying NOT NULL,
    label character varying,
    folder_id uuid NOT NULL,
    task_type character varying,
    assignees character varying[] DEFAULT ARRAY[]::character varying[] NOT NULL,
    thumbnail_id uuid,
    attrib jsonb DEFAULT '{}'::jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    active boolean DEFAULT true NOT NULL,
    status character varying NOT NULL,
    tags character varying[] DEFAULT ARRAY[]::character varying[] NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.tasks OWNER TO ayon;

--
-- Name: tasks_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.tasks_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.tasks_creation_order_seq OWNER TO ayon;

--
-- Name: tasks_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.tasks_creation_order_seq OWNED BY project_test_project.tasks.creation_order;


--
-- Name: thumbnails; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.thumbnails (
    id uuid NOT NULL,
    mime character varying NOT NULL,
    data bytea NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE ONLY project_test_project.thumbnails ALTER COLUMN data SET STORAGE EXTERNAL;


ALTER TABLE project_test_project.thumbnails OWNER TO ayon;

--
-- Name: versions; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.versions (
    id uuid NOT NULL,
    version integer NOT NULL,
    product_id uuid NOT NULL,
    task_id uuid,
    thumbnail_id uuid,
    author character varying,
    attrib jsonb DEFAULT '{}'::jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    active boolean DEFAULT true NOT NULL,
    status character varying NOT NULL,
    tags character varying[] DEFAULT ARRAY[]::character varying[] NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.versions OWNER TO ayon;

--
-- Name: version_list; Type: MATERIALIZED VIEW; Schema: project_test_project; Owner: ayon
--

CREATE MATERIALIZED VIEW project_test_project.version_list AS
 SELECT v.product_id,
    array_agg(v.id ORDER BY v.version) AS ids,
    array_agg(v.version ORDER BY v.version) AS versions
   FROM project_test_project.versions v
  GROUP BY v.product_id
  WITH NO DATA;


ALTER TABLE project_test_project.version_list OWNER TO ayon;

--
-- Name: versions_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.versions_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.versions_creation_order_seq OWNER TO ayon;

--
-- Name: versions_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.versions_creation_order_seq OWNED BY project_test_project.versions.creation_order;


--
-- Name: workfiles; Type: TABLE; Schema: project_test_project; Owner: ayon
--

CREATE TABLE project_test_project.workfiles (
    id uuid NOT NULL,
    path character varying NOT NULL,
    task_id uuid NOT NULL,
    thumbnail_id uuid,
    created_by character varying,
    updated_by character varying,
    attrib jsonb DEFAULT '{}'::jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    active boolean DEFAULT true NOT NULL,
    status character varying NOT NULL,
    tags character varying[] DEFAULT ARRAY[]::character varying[] NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    creation_order integer NOT NULL
);


ALTER TABLE project_test_project.workfiles OWNER TO ayon;

--
-- Name: workfiles_creation_order_seq; Type: SEQUENCE; Schema: project_test_project; Owner: ayon
--

CREATE SEQUENCE project_test_project.workfiles_creation_order_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_test_project.workfiles_creation_order_seq OWNER TO ayon;

--
-- Name: workfiles_creation_order_seq; Type: SEQUENCE OWNED BY; Schema: project_test_project; Owner: ayon
--

ALTER SEQUENCE project_test_project.workfiles_creation_order_seq OWNED BY project_test_project.workfiles.creation_order;


--
-- Name: activities creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.activities ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.activities_creation_order_seq'::regclass);


--
-- Name: activity_references creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.activity_references ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.activity_references_creation_order_seq'::regclass);


--
-- Name: folders creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.folders ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.folders_creation_order_seq'::regclass);


--
-- Name: links creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.links ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.links_creation_order_seq'::regclass);


--
-- Name: products creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.products ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.products_creation_order_seq'::regclass);


--
-- Name: representations creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.representations ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.representations_creation_order_seq'::regclass);


--
-- Name: tasks creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.tasks ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.tasks_creation_order_seq'::regclass);


--
-- Name: versions creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.versions ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.versions_creation_order_seq'::regclass);


--
-- Name: workfiles creation_order; Type: DEFAULT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles ALTER COLUMN creation_order SET DEFAULT nextval('project_test_project.workfiles_creation_order_seq'::regclass);


--
-- Data for Name: access_groups; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.access_groups (name, data) FROM stdin;
\.


--
-- Data for Name: activities; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.activities (id, activity_type, body, data, created_at, updated_at, creation_order) FROM stdin;
9ac766c0-1782-11ef-900e-0242ac120005	version.publish	Published [v001](version:9aa522de178211efb2f3d88083815492)	{"author": "admin", "origin": {"id": "9aa522de178211efb2f3d88083815492", "name": "v001", "type": "version"}, "context": {"taskId": "232931e016c711efbdec3bceaf68601a", "folderId": "16fb36c016c711efbdec3bceaf68601a", "taskName": "test_task", "taskType": "Generic", "productId": "9a9a4304178211ef8546d88083815492", "taskLabel": "test_task", "folderName": "test_asset", "folderPath": "test_asset", "folderLabel": "test_asset", "productName": "renderTest_taskMain", "productType": "render"}}	2024-05-21 14:58:38.161643+00	2024-05-21 14:58:38.161643+00	1
9ae67a7e-1782-11ef-900e-0242ac120005	version.publish	Published [v001](version:9ad1fc94178211efa1efd88083815492)	{"author": "admin", "origin": {"id": "9ad1fc94178211efa1efd88083815492", "name": "v001", "type": "version"}, "context": {"taskId": "232931e016c711efbdec3bceaf68601a", "folderId": "16fb36c016c711efbdec3bceaf68601a", "taskName": "test_task", "taskType": "Generic", "productId": "9ac80a4c178211efb05dd88083815492", "taskLabel": "test_task", "folderName": "test_asset", "folderPath": "test_asset", "folderLabel": "test_asset", "productName": "workfileTest_task", "productType": "workfile"}}	2024-05-21 14:58:38.37448+00	2024-05-21 14:58:38.37448+00	2
\.


--
-- Data for Name: activity_references; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.activity_references (id, activity_id, reference_type, entity_type, entity_id, entity_name, active, data, created_at, updated_at, creation_order) FROM stdin;
9ac5cfcc-1782-11ef-900e-0242ac120005	9ac766c0-1782-11ef-900e-0242ac120005	origin	version	9aa522de-1782-11ef-b2f3-d88083815492	\N	t	{}	2024-05-21 14:58:38.161643+00	2024-05-21 14:58:38.161643+00	1
9ac5d800-1782-11ef-900e-0242ac120005	9ac766c0-1782-11ef-900e-0242ac120005	relation	task	232931e0-16c7-11ef-bdec-3bceaf68601a	\N	t	{}	2024-05-21 14:58:38.161643+00	2024-05-21 14:58:38.161643+00	2
9ac5d26a-1782-11ef-900e-0242ac120005	9ac766c0-1782-11ef-900e-0242ac120005	author	user	\N	admin	t	{}	2024-05-21 14:58:38.161643+00	2024-05-21 14:58:38.161643+00	3
9ae64bda-1782-11ef-900e-0242ac120005	9ae67a7e-1782-11ef-900e-0242ac120005	author	user	\N	admin	t	{}	2024-05-21 14:58:38.37448+00	2024-05-21 14:58:38.37448+00	4
9ae650f8-1782-11ef-900e-0242ac120005	9ae67a7e-1782-11ef-900e-0242ac120005	relation	task	232931e0-16c7-11ef-bdec-3bceaf68601a	\N	t	{}	2024-05-21 14:58:38.37448+00	2024-05-21 14:58:38.37448+00	5
9ae64964-1782-11ef-900e-0242ac120005	9ae67a7e-1782-11ef-900e-0242ac120005	origin	version	9ad1fc94-1782-11ef-a1ef-d88083815492	\N	t	{}	2024-05-21 14:58:38.37448+00	2024-05-21 14:58:38.37448+00	6
\.


--
-- Data for Name: addon_data; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.addon_data (addon_name, addon_version, key, data) FROM stdin;
\.


--
-- Data for Name: custom_roots; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.custom_roots (site_id, user_name, data) FROM stdin;
\.


--
-- Data for Name: entity_paths; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.entity_paths (entity_id, entity_type, path) FROM stdin;
\.


--
-- Data for Name: exported_attributes; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.exported_attributes (folder_id, path, attrib) FROM stdin;
16fb36c0-16c7-11ef-bdec-3bceaf68601a	test_asset	{"fps": 25.0, "tools": [], "clipIn": 1, "clipOut": 1, "frameEnd": 1010, "handleEnd": 0, "frameStart": 1001, "handleStart": 0, "pixelAspect": 1.0, "applications": ["nuke/15-0", "nuke/13-0", "nuke/14-0", "nuke/13-2"], "resolutionWidth": 1920, "resolutionHeight": 1080}
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.files (id, size, author, activity_id, data, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: folder_types; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.folder_types (name, "position", data) FROM stdin;
Folder	1	{"icon": "folder", "name": "Folder", "shortName": ""}
Library	2	{"icon": "category", "name": "Library", "shortName": "lib"}
Asset	3	{"icon": "smart_toy", "name": "Asset", "shortName": ""}
Episode	4	{"icon": "live_tv", "name": "Episode", "shortName": "ep"}
Sequence	5	{"icon": "theaters", "name": "Sequence", "shortName": "sq"}
Shot	6	{"icon": "movie", "name": "Shot", "shortName": "sh"}
\.


--
-- Data for Name: folders; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.folders (id, name, label, folder_type, parent_id, thumbnail_id, attrib, data, status, tags, active, created_at, updated_at, creation_order) FROM stdin;
16fb36c0-16c7-11ef-bdec-3bceaf68601a	test_asset	test_asset	Asset	\N	\N	{"frameEnd": 1010}	{}	Not ready	{}	t	2024-05-20 16:36:44.217676+00	2024-05-22 11:34:34.838878+00	1
\.


--
-- Data for Name: link_types; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.link_types (name, input_type, output_type, link_type, data) FROM stdin;
generative|version|version	version	version	generative	{"color": "#2626e0", "style": "solid"}
breakdown|folder|folder	folder	folder	breakdown	{"color": "#27792a", "style": "solid"}
reference|version|version	version	version	reference	{"color": "#d94383", "style": "solid"}
template|folder|folder	folder	folder	template	{"color": "#d94383", "style": "solid"}
\.


--
-- Data for Name: links; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.links (id, name, link_type, input_id, output_id, author, data, created_at, creation_order) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.products (id, name, folder_id, product_type, attrib, data, active, status, tags, created_at, updated_at, creation_order) FROM stdin;
\.


--
-- Data for Name: project_site_settings; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.project_site_settings (addon_name, addon_version, site_id, user_name, data) FROM stdin;
\.


--
-- Data for Name: representations; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.representations (id, name, version_id, files, attrib, data, active, status, tags, created_at, updated_at, creation_order) FROM stdin;
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.settings (addon_name, addon_version, variant, data) FROM stdin;
\.


--
-- Data for Name: statuses; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.statuses (name, "position", data) FROM stdin;
Not ready	1	{"icon": "fiber_new", "name": "Not ready", "color": "#434a56", "state": "not_started", "shortName": "NRD"}
Ready to start	2	{"icon": "timer", "name": "Ready to start", "color": "#bababa", "state": "not_started", "shortName": "RDY"}
In progress	3	{"icon": "play_arrow", "name": "In progress", "color": "#3498db", "state": "in_progress", "shortName": "PRG"}
Pending review	4	{"icon": "visibility", "name": "Pending review", "color": "#ff9b0a", "state": "in_progress", "shortName": "RVW"}
Approved	5	{"icon": "task_alt", "name": "Approved", "color": "#00f0b4", "state": "done", "shortName": "APP"}
On hold	6	{"icon": "back_hand", "name": "On hold", "color": "#fa6e46", "state": "blocked", "shortName": "HLD"}
Omitted	7	{"icon": "block", "name": "Omitted", "color": "#cb1a1a", "state": "blocked", "shortName": "OMT"}
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.tags (name, "position", data) FROM stdin;
\.


--
-- Data for Name: task_types; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.task_types (name, "position", data) FROM stdin;
Generic	1	{"icon": "task_alt", "name": "Generic", "shortName": "gener"}
Art	2	{"icon": "palette", "name": "Art", "shortName": "art"}
Modeling	3	{"icon": "language", "name": "Modeling", "shortName": "mdl"}
Texture	4	{"icon": "brush", "name": "Texture", "shortName": "tex"}
Lookdev	5	{"icon": "ev_shadow", "name": "Lookdev", "shortName": "look"}
Rigging	6	{"icon": "construction", "name": "Rigging", "shortName": "rig"}
Edit	7	{"icon": "imagesearch_roller", "name": "Edit", "shortName": "edit"}
Layout	8	{"icon": "nature_people", "name": "Layout", "shortName": "lay"}
Setdress	9	{"icon": "scene", "name": "Setdress", "shortName": "dress"}
Animation	10	{"icon": "directions_run", "name": "Animation", "shortName": "anim"}
FX	11	{"icon": "fireplace", "name": "FX", "shortName": "fx"}
Lighting	12	{"icon": "highlight", "name": "Lighting", "shortName": "lgt"}
Paint	13	{"icon": "video_stable", "name": "Paint", "shortName": "paint"}
Compositing	14	{"icon": "layers", "name": "Compositing", "shortName": "comp"}
Roto	15	{"icon": "gesture", "name": "Roto", "shortName": "roto"}
Matchmove	16	{"icon": "switch_video", "name": "Matchmove", "shortName": "matchmove"}
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.tasks (id, name, label, folder_id, task_type, assignees, thumbnail_id, attrib, data, active, status, tags, created_at, updated_at, creation_order) FROM stdin;
232931e0-16c7-11ef-bdec-3bceaf68601a	test_task	test_task	16fb36c0-16c7-11ef-bdec-3bceaf68601a	Generic	{}	\N	{}	{}	t	Not ready	{}	2024-05-20 16:36:44.220094+00	2024-05-20 16:36:44.220099+00	1
\.


--
-- Data for Name: thumbnails; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.thumbnails (id, mime, data, created_at) FROM stdin;
\.


--
-- Data for Name: versions; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.versions (id, version, product_id, task_id, thumbnail_id, author, attrib, data, active, status, tags, created_at, updated_at, creation_order) FROM stdin;
\.


--
-- Data for Name: workfiles; Type: TABLE DATA; Schema: project_test_project; Owner: ayon
--

COPY project_test_project.workfiles (id, path, task_id, thumbnail_id, created_by, updated_by, attrib, data, active, status, tags, created_at, updated_at, creation_order) FROM stdin;
\.


--
-- Name: activities_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.activities_creation_order_seq', 2, true);


--
-- Name: activity_references_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.activity_references_creation_order_seq', 6, true);


--
-- Name: folders_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.folders_creation_order_seq', 1, true);


--
-- Name: links_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.links_creation_order_seq', 1, true);


--
-- Name: products_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.products_creation_order_seq', 2, true);


--
-- Name: representations_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.representations_creation_order_seq', 2, true);


--
-- Name: tasks_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.tasks_creation_order_seq', 1, true);


--
-- Name: versions_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.versions_creation_order_seq', 2, true);


--
-- Name: workfiles_creation_order_seq; Type: SEQUENCE SET; Schema: project_test_project; Owner: ayon
--

SELECT pg_catalog.setval('project_test_project.workfiles_creation_order_seq', 1, false);


--
-- Name: access_groups access_groups_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.access_groups
    ADD CONSTRAINT access_groups_pkey PRIMARY KEY (name);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: activity_references activity_references_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.activity_references
    ADD CONSTRAINT activity_references_pkey PRIMARY KEY (id);


--
-- Name: addon_data addon_data_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.addon_data
    ADD CONSTRAINT addon_data_pkey PRIMARY KEY (addon_name, addon_version, key);


--
-- Name: custom_roots custom_roots_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.custom_roots
    ADD CONSTRAINT custom_roots_pkey PRIMARY KEY (site_id, user_name);


--
-- Name: entity_paths entity_paths_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.entity_paths
    ADD CONSTRAINT entity_paths_pkey PRIMARY KEY (entity_id);


--
-- Name: exported_attributes exported_attributes_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.exported_attributes
    ADD CONSTRAINT exported_attributes_pkey PRIMARY KEY (folder_id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: folder_types folder_types_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.folder_types
    ADD CONSTRAINT folder_types_pkey PRIMARY KEY (name);


--
-- Name: folders folders_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.folders
    ADD CONSTRAINT folders_pkey PRIMARY KEY (id);


--
-- Name: link_types link_types_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.link_types
    ADD CONSTRAINT link_types_pkey PRIMARY KEY (name);


--
-- Name: links links_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: project_site_settings project_site_settings_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.project_site_settings
    ADD CONSTRAINT project_site_settings_pkey PRIMARY KEY (addon_name, addon_version, site_id, user_name);


--
-- Name: representations representations_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.representations
    ADD CONSTRAINT representations_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (addon_name, addon_version, variant);


--
-- Name: statuses statuses_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.statuses
    ADD CONSTRAINT statuses_pkey PRIMARY KEY (name);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (name);


--
-- Name: task_types task_types_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.task_types
    ADD CONSTRAINT task_types_pkey PRIMARY KEY (name);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: thumbnails thumbnails_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.thumbnails
    ADD CONSTRAINT thumbnails_pkey PRIMARY KEY (id);


--
-- Name: versions versions_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.versions
    ADD CONSTRAINT versions_pkey PRIMARY KEY (id);


--
-- Name: workfiles workfiles_path_key; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles
    ADD CONSTRAINT workfiles_path_key UNIQUE (path);


--
-- Name: workfiles workfiles_pkey; Type: CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles
    ADD CONSTRAINT workfiles_pkey PRIMARY KEY (id);


--
-- Name: entity_paths_path_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX entity_paths_path_idx ON project_test_project.entity_paths USING gin (path public.gin_trgm_ops);


--
-- Name: folder_creation_order_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX folder_creation_order_idx ON project_test_project.folders USING btree (creation_order);


--
-- Name: folder_parent_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX folder_parent_idx ON project_test_project.folders USING btree (parent_id);


--
-- Name: folder_root_unique_name; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX folder_root_unique_name ON project_test_project.folders USING btree (name) WHERE ((active IS TRUE) AND (parent_id IS NULL));


--
-- Name: folder_unique_name_parent; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX folder_unique_name_parent ON project_test_project.folders USING btree (parent_id, name) WHERE ((active IS TRUE) AND (parent_id IS NOT NULL));


--
-- Name: hierarchy_id; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX hierarchy_id ON project_test_project.hierarchy USING btree (id);


--
-- Name: idx_activity_entity_id; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX idx_activity_entity_id ON project_test_project.activity_references USING btree (entity_id);


--
-- Name: idx_activity_id; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX idx_activity_id ON project_test_project.activity_references USING btree (activity_id);


--
-- Name: idx_activity_reference_created_at; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX idx_activity_reference_created_at ON project_test_project.activity_references USING btree (created_at);


--
-- Name: idx_activity_reference_unique; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX idx_activity_reference_unique ON project_test_project.activity_references USING btree (activity_id, entity_id, entity_name, reference_type);


--
-- Name: idx_activity_type; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX idx_activity_type ON project_test_project.activities USING btree (activity_type);


--
-- Name: idx_files_activity_id; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX idx_files_activity_id ON project_test_project.files USING btree (activity_id);


--
-- Name: link_creation_order_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX link_creation_order_idx ON project_test_project.links USING btree (creation_order);


--
-- Name: link_input_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX link_input_idx ON project_test_project.links USING btree (input_id);


--
-- Name: link_output_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX link_output_idx ON project_test_project.links USING btree (output_id);


--
-- Name: link_type_unique_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX link_type_unique_idx ON project_test_project.link_types USING btree (input_type, output_type, link_type);


--
-- Name: product_creation_order_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX product_creation_order_idx ON project_test_project.products USING btree (creation_order);


--
-- Name: product_parent_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX product_parent_idx ON project_test_project.products USING btree (folder_id);


--
-- Name: product_type_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX product_type_idx ON project_test_project.products USING btree (product_type);


--
-- Name: product_unique_name_parent; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX product_unique_name_parent ON project_test_project.products USING btree (folder_id, name) WHERE (active IS TRUE);


--
-- Name: representation_creation_order_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX representation_creation_order_idx ON project_test_project.representations USING btree (creation_order);


--
-- Name: representation_parent_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX representation_parent_idx ON project_test_project.representations USING btree (version_id);


--
-- Name: representation_unique_name_on_version; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX representation_unique_name_on_version ON project_test_project.representations USING btree (version_id, name) WHERE (active IS TRUE);


--
-- Name: task_creation_order_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX task_creation_order_idx ON project_test_project.tasks USING btree (creation_order);


--
-- Name: task_parent_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX task_parent_idx ON project_test_project.tasks USING btree (folder_id);


--
-- Name: task_type_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX task_type_idx ON project_test_project.tasks USING btree (task_type);


--
-- Name: task_unique_name; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX task_unique_name ON project_test_project.tasks USING btree (folder_id, name);


--
-- Name: version_creation_order_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX version_creation_order_idx ON project_test_project.versions USING btree (creation_order);


--
-- Name: version_list_id; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX version_list_id ON project_test_project.version_list USING btree (product_id);


--
-- Name: version_parent_idx; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE INDEX version_parent_idx ON project_test_project.versions USING btree (product_id);


--
-- Name: version_unique_version_parent; Type: INDEX; Schema: project_test_project; Owner: ayon
--

CREATE UNIQUE INDEX version_unique_version_parent ON project_test_project.versions USING btree (product_id, version) WHERE (active IS TRUE);


--
-- Name: access_groups access_groups_name_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.access_groups
    ADD CONSTRAINT access_groups_name_fkey FOREIGN KEY (name) REFERENCES public.access_groups(name) ON DELETE CASCADE;


--
-- Name: activity_references activity_references_activity_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.activity_references
    ADD CONSTRAINT activity_references_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES project_test_project.activities(id) ON DELETE CASCADE;


--
-- Name: custom_roots custom_roots_site_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.custom_roots
    ADD CONSTRAINT custom_roots_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON DELETE CASCADE;


--
-- Name: custom_roots custom_roots_user_name_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.custom_roots
    ADD CONSTRAINT custom_roots_user_name_fkey FOREIGN KEY (user_name) REFERENCES public.users(name) ON DELETE CASCADE;


--
-- Name: exported_attributes exported_attributes_folder_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.exported_attributes
    ADD CONSTRAINT exported_attributes_folder_id_fkey FOREIGN KEY (folder_id) REFERENCES project_test_project.folders(id) ON DELETE CASCADE;


--
-- Name: files files_activity_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.files
    ADD CONSTRAINT files_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES project_test_project.activities(id) ON DELETE SET NULL;


--
-- Name: files files_author_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.files
    ADD CONSTRAINT files_author_fkey FOREIGN KEY (author) REFERENCES public.users(name) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: folders folders_folder_type_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.folders
    ADD CONSTRAINT folders_folder_type_fkey FOREIGN KEY (folder_type) REFERENCES project_test_project.folder_types(name) ON UPDATE CASCADE;


--
-- Name: folders folders_parent_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.folders
    ADD CONSTRAINT folders_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES project_test_project.folders(id) ON DELETE CASCADE;


--
-- Name: folders folders_status_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.folders
    ADD CONSTRAINT folders_status_fkey FOREIGN KEY (status) REFERENCES project_test_project.statuses(name) ON UPDATE CASCADE;


--
-- Name: folders folders_thumbnail_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.folders
    ADD CONSTRAINT folders_thumbnail_id_fkey FOREIGN KEY (thumbnail_id) REFERENCES project_test_project.thumbnails(id) ON DELETE SET NULL;


--
-- Name: links links_link_type_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.links
    ADD CONSTRAINT links_link_type_fkey FOREIGN KEY (link_type) REFERENCES project_test_project.link_types(name) ON DELETE CASCADE;


--
-- Name: products products_folder_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.products
    ADD CONSTRAINT products_folder_id_fkey FOREIGN KEY (folder_id) REFERENCES project_test_project.folders(id);


--
-- Name: products products_product_type_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.products
    ADD CONSTRAINT products_product_type_fkey FOREIGN KEY (product_type) REFERENCES public.product_types(name) ON UPDATE CASCADE;


--
-- Name: products products_status_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.products
    ADD CONSTRAINT products_status_fkey FOREIGN KEY (status) REFERENCES project_test_project.statuses(name) ON UPDATE CASCADE;


--
-- Name: project_site_settings project_site_settings_site_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.project_site_settings
    ADD CONSTRAINT project_site_settings_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON DELETE CASCADE;


--
-- Name: project_site_settings project_site_settings_user_name_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.project_site_settings
    ADD CONSTRAINT project_site_settings_user_name_fkey FOREIGN KEY (user_name) REFERENCES public.users(name) ON DELETE CASCADE;


--
-- Name: representations representations_status_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.representations
    ADD CONSTRAINT representations_status_fkey FOREIGN KEY (status) REFERENCES project_test_project.statuses(name) ON UPDATE CASCADE;


--
-- Name: representations representations_version_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.representations
    ADD CONSTRAINT representations_version_id_fkey FOREIGN KEY (version_id) REFERENCES project_test_project.versions(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_folder_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.tasks
    ADD CONSTRAINT tasks_folder_id_fkey FOREIGN KEY (folder_id) REFERENCES project_test_project.folders(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_status_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.tasks
    ADD CONSTRAINT tasks_status_fkey FOREIGN KEY (status) REFERENCES project_test_project.statuses(name) ON UPDATE CASCADE;


--
-- Name: tasks tasks_task_type_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.tasks
    ADD CONSTRAINT tasks_task_type_fkey FOREIGN KEY (task_type) REFERENCES project_test_project.task_types(name) ON UPDATE CASCADE;


--
-- Name: tasks tasks_thumbnail_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.tasks
    ADD CONSTRAINT tasks_thumbnail_id_fkey FOREIGN KEY (thumbnail_id) REFERENCES project_test_project.thumbnails(id) ON DELETE SET NULL;


--
-- Name: versions versions_product_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.versions
    ADD CONSTRAINT versions_product_id_fkey FOREIGN KEY (product_id) REFERENCES project_test_project.products(id) ON DELETE CASCADE;


--
-- Name: versions versions_status_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.versions
    ADD CONSTRAINT versions_status_fkey FOREIGN KEY (status) REFERENCES project_test_project.statuses(name) ON UPDATE CASCADE;


--
-- Name: versions versions_task_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.versions
    ADD CONSTRAINT versions_task_id_fkey FOREIGN KEY (task_id) REFERENCES project_test_project.tasks(id) ON DELETE SET NULL;


--
-- Name: versions versions_thumbnail_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.versions
    ADD CONSTRAINT versions_thumbnail_id_fkey FOREIGN KEY (thumbnail_id) REFERENCES project_test_project.thumbnails(id) ON DELETE SET NULL;


--
-- Name: workfiles workfiles_created_by_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles
    ADD CONSTRAINT workfiles_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(name) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: workfiles workfiles_status_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles
    ADD CONSTRAINT workfiles_status_fkey FOREIGN KEY (status) REFERENCES project_test_project.statuses(name) ON UPDATE CASCADE;


--
-- Name: workfiles workfiles_task_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles
    ADD CONSTRAINT workfiles_task_id_fkey FOREIGN KEY (task_id) REFERENCES project_test_project.tasks(id) ON DELETE CASCADE;


--
-- Name: workfiles workfiles_thumbnail_id_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles
    ADD CONSTRAINT workfiles_thumbnail_id_fkey FOREIGN KEY (thumbnail_id) REFERENCES project_test_project.thumbnails(id) ON DELETE SET NULL;


--
-- Name: workfiles workfiles_updated_by_fkey; Type: FK CONSTRAINT; Schema: project_test_project; Owner: ayon
--

ALTER TABLE ONLY project_test_project.workfiles
    ADD CONSTRAINT workfiles_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(name) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: hierarchy; Type: MATERIALIZED VIEW DATA; Schema: project_test_project; Owner: ayon
--

REFRESH MATERIALIZED VIEW project_test_project.hierarchy;


--
-- Name: version_list; Type: MATERIALIZED VIEW DATA; Schema: project_test_project; Owner: ayon
--

REFRESH MATERIALIZED VIEW project_test_project.version_list;


--
-- PostgreSQL database dump complete
--

