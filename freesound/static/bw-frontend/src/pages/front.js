import './page-polyfills'
import throttle from 'lodash.throttle'
import navbar from '../components/navbar'
import { addTypeAheadFeatures } from '../components/typeahead'
import tippy from 'tippy.js'

const heroSearch = document.getElementsByClassName('bw-front__hero-search')[0]

const input = document.getElementById('search-sounds')

const SCROLL_CHECK_TIMER = 100 // min interval (in ms) between consecutive calls of scroll checking function
const checkShouldShowSearchInNavbar = throttle(() => {
  const heroRect = heroSearch.getBoundingClientRect()
  // not all browsers support clientRect.height
  const heroSearchPosition = heroRect.height
    ? heroRect.y + heroRect.height
    : heroRect.y
  const shouldShowSearchBar = heroSearchPosition < 80
  const isShowingSearchBar = !navbar.classList.contains('bw-nav--expanded')
  if (shouldShowSearchBar !== isShowingSearchBar) {
    navbar.classList.toggle('bw-nav--expanded')
  }
}, SCROLL_CHECK_TIMER)

window.addEventListener('scroll', checkShouldShowSearchInNavbar)

const query_suggestions_url = process.env.QUERY_SUGGESTIONS_URL

const fetchSuggestions = async query => {
  let response = await fetch(`${query_suggestions_url}?q=${input.value}`)
  let data = await response.json()
  const suggestions = data.suggestions
  return suggestions
}

addTypeAheadFeatures(input, fetchSuggestions)


tippy('#sound-of-the-day-carousel .carousel-right', {
  content: 'Guess a new sound'
})
