-- CREATE SCHEMA IF NOT EXISTS content;


-- ALTER SCHEMA content OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: film_work; Type: TABLE; Schema: content; Owner: postgres
--

CREATE TABLE users (
    id uuid NOT NULL,
    full_name text NOT NULL,
    password text NOT NULL,
    -- description text,
    -- creation_date date,
    -- rating double precision,
    -- type text NOT NULL,
    -- created timestamp without time zone,
    -- modified timestamp without time zone
);


ALTER TABLE users OWNER TO postgres;
