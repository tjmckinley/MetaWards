#' metawards: Metapopulation Disease Modelling
#'
#' This package provides a convenient R wrapper around the Python
#' metawards package. For more information about MetaWards see
#' \url{https://metawards.org}. For a quick-start guide see
#' \url{https://metawards.org/quickstart}.
#'
#' This package uses reticulate to automatically load and wrap
#' the Python metawards package. The easiest way to install metawards
#' is to run the \code{\link{py_install_metawards}} function. This will
#' install metawards into the default python associated with
#' reticulate. Alternatively, you can install python manually into
#' your own python environment and then tell reticulate to use
#' that python so that it can find the metawards module.
#'
#' @section Python functions:
#' The python functions that are wrapped are all documented
#' at \url{https://metawards.org/api}.
#'
#' @section R-specific functions:
#' \itemize{
#' \item \code{\link{py_install_metawards}}
#' \item \code{\link{py_metawards_available}}
#' \item \code{\link{py_version_metawards}}
#' }
#'
#' @docType package
#' @name metawards
NULL

#' @export
metawards <- NULL

.onLoad <- function(libname, pkgname){
  metawards <<- reticulate::import("metawards", delay_load = TRUE)
}

#' Install the metawards python module
#'
#' @param method The installation method to use (see reticulate). Defaults
#'               to auto, which means that it will install into the
#'               main environment (no conda-env or pipenv)
#' @param python_version The version of Python to use. This will be
#'                       be automatically set, and should be greater
#'                       than or equal to 3.7. Only use if you want to force
#'                       a particular python version to be used.
#' @return NULL
#' @export
py_install_metawards <- function(method = "auto", python_version = NULL){
  # get the current python version
  py_version <- reticulate::py_config()["version"]

  if (py_version < 3.7){
    py_version = 3.7
  }

  if (is.null(python_version)){
    python_version = py_version
  }
  else if (python_version < 3.7){
    python_version = py_version
  }

  reticulate::py_install("metawards==1.3.0", method = method,
                         python_version = python_version,
                         pip = TRUE)
}

#' Return whether MetaWards is installed and available
#'
#' @return Boolean of whether MetaWards is installed
#' @export
py_metawards_available <- function(){
  return(reticulate::py_module_available("metawards"))
}

#' Return the version number of the installed MetaWards module
#'
#' @return The version number as a string
#' @export
py_version_metawards <- function(){
  return(reticulate::py_to_r(
    reticulate::py_get_attr(metawards, "__version__")))
}
