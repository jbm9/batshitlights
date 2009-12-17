/* Turn anything with RGB greater than 50% grey into 50% grey;
   this gets rid of That Bastard Sun washing out the windows
   during the day, for the most part.  -jbm */

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

#include "camserv.h"
#include "camconfig.h"
#include "video.h"
#include "filter.h"
#include "log.h"

#define MODNAME "jbmfilter"

typedef struct jbm_filter_st {
} JbmFilter;


/*
 * filter_init:  Standard filter initialization routine.
 *
 * Filter variables:  randmod_perline = max # of random pixels per line
 *                    randmod_colordpix = Use colored pixels
 */

void *filter_init( CamConfig *ccfg, char *section_name ){
  JbmFilter *res;

  if( (res = malloc( sizeof( *res ))) == NULL ){
    camserv_log( MODNAME, 
		 "FATAL!  Could not allocate space for random filter!" );
    return NULL;
  }
  return res;
}

/*
 * filter_deinit:  Standard filter deinit routine 
 */

void filter_deinit( void *filter_dat ){
  JbmFilter *rfilt = filter_dat;

  free( rfilt );
}

void filter_func( char *in_data, char **out_data, void *cldat, 
		  const Video_Info *vinfo_in, Video_Info *vinfo_out )
{
  JbmFilter *rfilt = cldat;
  int rowspan, i, j, randval;
  unsigned char *cp, *outp;

  *vinfo_out = *vinfo_in;
  *out_data = in_data;

  if( vinfo_in->is_black_white ) { /* UNTESTED */
    rowspan = vinfo_in->width;
    
    for( i=0, cp = in_data; i< vinfo_in->height; i++, cp += rowspan ) {
      randval = random() % 100;
      for( j=0; j< randval; j++ ){
	outp = cp + (random() % vinfo_in->width );
	*outp = random() % 256;
      }
    }
  } else {
    rowspan = vinfo_in->width * 3;

    for( i=0, cp = in_data; i< vinfo_in->height; i++, cp += rowspan ){
      outp = (*out_data) + i*rowspan;
#if 0
      if (i % 2 == 0) {
        for (j = 0; j < rowspan; j += 3) {
          outp[j + 0] = 255 - outp[j+0];
          outp[j + 1] = 255 - outp[j+1];
          outp[j + 2] = 255 - outp[j+2];
        }
      }
#endif
      for( j=0; j < rowspan; j += 3 ) {
        if (
          outp[j + 0] > 128 &&
          outp[j + 1] > 128 &&
          outp[j + 2] > 128  )
           { 
          outp[j + 0] = 128;
          outp[j + 1] = 128;
          outp[j + 2] = 128;
           }

      }
    }
  }
}

void filter_validation(){
  Filter_Init_Func init = filter_init;
  Filter_Deinit_Func deinit = filter_deinit;
  Filter_Func_Func func = filter_func;

  if( init != NULL && deinit != NULL && func != NULL ) return;
}



/*
 * modinfo_query:  Routine to return information about the variables
 *                 accessed by this particular module.
 *
 * Return values:  Returns a malloced ModInfo structure, for which
 *                 the caller must free, or NULL on failure.
 */

ModInfo *modinfo_query(){
  ModInfo *res;

  if( (res = modinfo_create( 2 )) == NULL )
    return NULL;

  modinfo_varname_set( res, 0, "num_perline" );
  modinfo_desc_set( res, 0, "Maximum number of speckles per line" );
  res->vars[ 0 ].type = MODINFO_TYPE_INT;

  modinfo_varname_set( res, 1, "coloredpix" );
  modinfo_desc_set( res, 1, "Enable colored pixels (1==on, 0==off)");
  res->vars[ 1 ].type = MODINFO_TYPE_INT;

  return res;
}
