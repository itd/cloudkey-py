#/usr/bin/env python

from cloudkey.media import Media
import simplejson as json

media = Media('sebest', 'sebest', 'http://dc_api.sebest.dev.dailymotion.com')

# We upload one of our video
media_info = media.upload('/home/sebest/Videos/i_am_legend-tlr2_h1080p.mov')
media_url = media_info['url']

media.publish(url=media_url, presets=['flv_h263_mp3', 'mp4_h264_aac', 'flv_h263_mp3_ld'])
