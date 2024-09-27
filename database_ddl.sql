CREATE SCHEMA IF NOT EXISTS content;


ALTER SCHEMA content OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: film_work; Type: TABLE; Schema: content; Owner: postgres
--

CREATE TABLE content.users (
    id uuid NOT NULL,
    login VARCHAR NOT NULL,
    password TEXT NOT NULL
);


ALTER TABLE content.users OWNER TO postgres;