import type { components } from "./generated/openapi";

export type { components, operations, paths } from "./generated/openapi";

export type HealthResponse = components["schemas"]["HealthResponse"];
export type StatusResponse = components["schemas"]["StatusResponse"];

export type HomeResponse = components["schemas"]["HomeResponse"];
export type HomeSections = components["schemas"]["HomeSections"];
export type HomeItem = components["schemas"]["HomeItem"];
export type HomeRating = components["schemas"]["HomeRating"];
export type HomeMediaGap = components["schemas"]["HomeMediaGap"];

export type HomeExternalRating = components["schemas"]["HomeExternalRating"];
export type HomeTrailer = components["schemas"]["HomeTrailer"];
export type HomeHeroExperience = components["schemas"]["HomeHeroExperience"];
export type HomeRailResponse = components["schemas"]["HomeRailResponse"];
export type HomeTrailerCard = components["schemas"]["HomeTrailerCard"];
export type HomeTrailerRailResponse = components["schemas"]["HomeTrailerRailResponse"];
export type HomeSearchSuggestion = components["schemas"]["HomeSearchSuggestion"];
export type HomeSearchResponse = components["schemas"]["HomeSearchResponse"];
export type HomeGenreEntry = components["schemas"]["HomeGenreEntry"];
export type HomeGenresResponse = components["schemas"]["HomeGenresResponse"];

export type CatalogBrowseResponse = components["schemas"]["CatalogBrowseResponse"];
export type CatalogMediaSummary = components["schemas"]["CatalogMediaSummary"];
export type CatalogPersonResponse = components["schemas"]["CatalogPersonResponse"];
export type CatalogReviewsResponse = components["schemas"]["CatalogReviewsResponse"];
export type CatalogSeasonResponse = components["schemas"]["CatalogSeasonResponse"];
export type CatalogTitleResponse = components["schemas"]["CatalogTitleResponse"];
