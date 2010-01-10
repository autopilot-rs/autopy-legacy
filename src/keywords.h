#pragma once
#ifndef KEYWORDS_H
#define KEYWORDS_H

#if !defined(IS_C99) && (defined(SIZE_MAX) || defined(WCHAR_MAX) || \
	                     defined(_WCHAR_T) || defined(_WCHAR_T_DEFINED))
	#define IS_C99
#endif

/* A portable keyword for suggesting a function should be inlined. */
#ifndef INLINE
	#if defined(_MSC_VER)
		#define INLINE /* GFY, MSVC. Why is _inline so buggy?! */
	#elif defined(__GNUC__) || defined(__inline__)
		#define INLINE __inline__ /* gcc keyword */
	#elif defined(IS_C99) || defined(__MWERKS__) || \
	    (defined(__GNUC_STDC_H_INLINE__) && __GNUC_STDC_H_INLINE__)
		#define INLINE inline /* Official ANSI C99 keyword */
	#else
		#define INLINE /* Inline keyword unsupported */
	#endif
#endif

/* A complicated, portable model for declaring inline functions in
 * header files.
 * See http://www.greenend.org.uk/rjk/2003/03/inline.html. */
#ifndef H_INLINE
	#if (defined(__GNUC__) && __GNUC__) && \
        (!defined(__GNUC_STDC_H_INLINE__) || !__GNUC_STDC_H_INLINE__)
		#define H_INLINE extern INLINE /* GNU C89 inline */
	#elif (defined(__GNUC_STDC_H_INLINE__) && __GNUC_STDC_H_INLINE__) || \
	       defined(_C99_)
		#define H_INLINE INLINE /* C99 inline */
	#else
		#define H_INLINE static INLINE /* Fallback */
	#endif
#endif /* H_INLINE */

#endif /* KEYWORDS_H */
