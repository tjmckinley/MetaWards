context("MetaWards")
library(metawards)

# helper function to skip tests if we don't have the 'metawards' module
skip_if_no_metawards <- function() {
  have_metawards <- reticulate::py_module_available("metawards")
  if (!have_metawards)
    skip("metawards not available for testing")
}

test_that("metawards is loaded", {
  skip_if_no_metawards()
  expect_equal(py_metawards_available(), TRUE)
})

test_that("metawards can run", {
  skip_if_no_metawards()
  ward <- metawards$Ward(name="test")
  expect_equal(ward$name(), "test")
})
