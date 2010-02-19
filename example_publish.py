#/usr/bin/env python

from dcapi import DcAPI
import simplejson as json

c = DcApi('sebest', 'sebest', 'dk_api.sebest.dev.dailymotion.com')

# We upload one of our video
media_info = c.media_upload('/home/sebest/Videos/i_am_legend-tlr2_h1080p.mov')
media_url = media_info['url']

c.tool_publish(url=media_url, presets=['flv_h263_mp3', 'mp4_h264_aac', 'flv_h263_mp3_ld'])
