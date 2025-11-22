# MicroService2
People / Movies


## 1. Database (Cloud SQL)
Data is form IMDB public database. We get the 200 movie data, corresponding actor/director data, and the relationship data

* `movies`:
	* `id`, `title`, `genre`, `year`, `created_at`, `updated_at`, `version` (for ETag), `processing_status`.
* `people`:
	* `id`, `name`, `role`, `created_at`, `updated_at`.
* `movie_people`:
	* `movie_id`, `person_id`, `character_name`, `role_type`.


## 2. Implement (Cloud Run)
1.  **Real CRUD logic for Movies & People**
	* Implement full CRUD for `/movies` and `/people`.
2.  **Query Parameters for All Collections**
	* `GET /movies` Filtering: `title`, `genre`, `year`, `year_min`, `year_max`. Sorting: `sort`, `order`.
	* `GET /people` Filtering: `name`, `role`, `movie_id`.
	* Ensure **all collection endpoints** accept and correctly process query params.
3.  **Pagination Implementation**
	* `GET /movies` and `GET /people`: Support `page`, `page_size`, and return metadata.
4.  **eTag Handling**
	* For `GET /movies/{id}`: Compute ETag. Implement `If-None-Match` to return **`304 Not Modified`**.
5.  **Linked Data & Relative Paths**
	* Use `_links` object with **relative** URLs (e.g., `/movies/123/people`).
	* Implement proxy call for `GET /movies/{id}/people`, `GET /people/{id}/movies`.
6.  **201 Created for POST**
	* Implement **synchronous** `POST /movies` and `POST /people` to return **201 Created** with the `Location` header.
7.  **202 Accepted + Asynchronous Implementation + Polling**
	* Implement **asynchronous task processing** for `POST /movies/{movie_id}/generate-share-card`.
	* Return **202 Accepted** with `job_id` and `status_url` for polling.
	* Implement `GET /movies/{movie_id}/share-card-jobs/{job_id}` to check job status and retrieve the generated card URL upon completion.