# MetaWards
#
# This is a simple wrapper around the Python MetaWards package.
# This aims to simplify the installation of MetaWards in R.
#
# You can learn more about MetaWards at
#
#   https://metawards.org

metawards <- NULL

.onLoad <- function(libname, pkgname){
  metawards <<- reticulate::import("metawards", delay_load = TRUE)
}

install_metawards <- function(method = "auto", python_version = 3.7){
  reticulate::py_install("metawards==1.3.0", method = method,
                         python_version = python_version,
                         pip = TRUE)
}

is_metawards_available <- function(){
  return(reticulate::py_module_available("metawards"))
}


