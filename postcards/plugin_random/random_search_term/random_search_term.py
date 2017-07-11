from js2py.pyjs import *


def get_random_search_term():
    """
    this is an auto-conversion from javascript to python done with https://piter.io/projects/js2py
    original javascript sourcecode is copied from Random Personal Picture Finder script by Dave Mattson diddly.com
    http://www.diddly.com/random/
    note by author: "Feel free to copy this code, it sucks though"

    Probably the ugliest code I ever distributed on the internet :D
    :return: search term

    """

    # setting scope
    var = Scope(JS_BUILTINS)
    set_global_object(var)

    # Code follows:
    var.registers([u'fmt00000', u'getRandomIndex', u'generateFileName'])

    @Js
    def PyJsHoisted_fmt00000_(x, width, this, arguments, var=var):
        var = Scope({u'this': this, u'x': x, u'arguments': arguments, u'width': width}, var)
        var.registers([u'i', u'x', u'width'])
        var.put(u'count', Js(0.0))
        if (var.get(u'Math').callprop(u'abs', var.get(u'parseInt')(var.get(u'x'), Js(10.0))) < Js(100000.0)):
            if (var.get(u'Math').callprop(u'abs', var.get(u'parseInt')(var.get(u'x'), Js(10.0))) < Js(10000.0)):
                if (var.get(u'Math').callprop(u'abs', var.get(u'parseInt')(var.get(u'x'), Js(10.0))) < Js(1000.0)):
                    if (var.get(u'Math').callprop(u'abs', var.get(u'parseInt')(var.get(u'x'), Js(10.0))) < Js(100.0)):
                        if (var.get(u'Math').callprop(u'abs', var.get(u'parseInt')(var.get(u'x'), Js(10.0))) < Js(
                                10.0)):
                            if (var.get(u'width') > Js(1.0)):
                                (var.put(u'count', Js(var.get(u'count').to_number()) + Js(1)) - Js(1))
                        if (var.get(u'width') > Js(2.0)):
                            (var.put(u'count', Js(var.get(u'count').to_number()) + Js(1)) - Js(1))
                    if (var.get(u'width') > Js(3.0)):
                        (var.put(u'count', Js(var.get(u'count').to_number()) + Js(1)) - Js(1))
                if (var.get(u'width') > Js(4.0)):
                    (var.put(u'count', Js(var.get(u'count').to_number()) + Js(1)) - Js(1))
        # for JS loop
        var.put(u'i', Js(0.0))
        while (var.get(u'i') < var.get(u'count')):
            try:
                var.put(u'x', (Js(u'0') + var.get(u'x')))
            finally:
                (var.put(u'i', Js(var.get(u'i').to_number()) + Js(1)) - Js(1))
        return var.get(u'x')

    PyJsHoisted_fmt00000_.func_name = u'fmt00000'
    var.put(u'fmt00000', PyJsHoisted_fmt00000_)

    @Js
    def PyJsHoisted_getRandomIndex_(max, this, arguments, var=var):
        var = Scope({u'this': this, u'max': max, u'arguments': arguments}, var)
        var.registers([u'max', u'randomNum'])
        var.put(u'randomNum', var.get(u'Math').callprop(u'random'))
        var.put(u'randomNum', (var.get(u'randomNum') * var.get(u'max')))
        var.put(u'randomNum', var.get(u'parseInt')(var.get(u'randomNum')))
        if var.get(u'isNaN')(var.get(u'randomNum')):
            var.put(u'randomNum', Js(0.0))
        return var.get(u'randomNum')

    PyJsHoisted_getRandomIndex_.func_name = u'getRandomIndex'
    var.put(u'getRandomIndex', PyJsHoisted_getRandomIndex_)

    @Js
    def PyJsHoisted_generateFileName_(this, arguments, var=var):
        var = Scope({u'this': this, u'arguments': arguments}, var)
        var.registers([u'cams', u'choice', u'width', u'range', u'types', u'size'])
        var.put(u'types', Js(26.0))
        var.put(u'cams', var.get(u'Array').create(var.get(u'types')))
        var.get(u'cams').put(u'0', Js(u'dcp0'))
        var.get(u'cams').put(u'1', Js(u'dsc0'))
        var.get(u'cams').put(u'2', Js(u'dscn'))
        var.get(u'cams').put(u'3', Js(u'mvc-'))
        var.get(u'cams').put(u'4', Js(u'mvc0'))
        var.get(u'cams').put(u'5', Js(u'P101'))
        var.get(u'cams').put(u'6', Js(u'P'))
        var.get(u'cams').put(u'7', Js(u'IMG_'))
        var.get(u'cams').put(u'8', Js(u'imag'))
        var.get(u'cams').put(u'9', Js(u'1'))
        var.get(u'cams').put(u'10', Js(u'dscf'))
        var.get(u'cams').put(u'11', Js(u'pdrm'))
        var.get(u'cams').put(u'12', Js(u'IM00'))
        var.get(u'cams').put(u'13', Js(u'EX00'))
        var.get(u'cams').put(u'14', Js(u'dc'))
        var.get(u'cams').put(u'15', Js(u'pict'))
        var.get(u'cams').put(u'16', Js(u'P00'))
        var.get(u'cams').put(u'17', Js(u''))
        var.get(u'cams').put(u'18', Js(u''))
        var.get(u'cams').put(u'19', Js(u'imgp'))
        var.get(u'cams').put(u'20', Js(u'pana'))
        var.get(u'cams').put(u'21', Js(u'1'))
        var.get(u'cams').put(u'22', Js(u'HPIM'))
        var.get(u'cams').put(u'23', Js(u'PCDV'))
        var.get(u'cams').put(u'24', Js(u'_MG_'))
        var.get(u'cams').put(u'25', Js(u'IMG_'))
        var.put(u'size', Js(u''))
        var.put(u'range', Js(4000.0))
        var.put(u'width', Js(4.0))
        var.put(u'choice', var.get(u'getRandomIndex')(var.get(u'types')))
        var.put(u'str', var.get(u'cams').get(var.get(u'choice')))
        if (var.get(u'choice') == Js(3.0)):
            var.put(u'range', Js(400.0))
            var.put(u'width', Js(3.0))
        if (var.get(u'choice') == Js(4.0)):
            var.put(u'range', Js(500.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(6.0)):
            var.put(u'range', Js(50.0))
            var.put(u'width', Js(4.0))
            var.put(u'strmonth', var.get(u'getRandomIndex')(Js(13.0)))
            if (var.get(u'strmonth') == Js(10.0)):
                var.put(u'strmonth', Js(u'a'))
            if (var.get(u'strmonth') == Js(11.0)):
                var.put(u'strmonth', Js(u'b'))
            if (var.get(u'strmonth') == Js(12.0)):
                var.put(u'strmonth', Js(u'c'))
            var.put(u'strdate', var.get(u'getRandomIndex')(Js(31.0)))
            var.put(u'strdate', var.get(u'fmt00000')(var.get(u'strdate'), Js(2.0)))
            var.put(u'str', var.get(u'strmonth'), u'+')
            var.put(u'str', var.get(u'strdate'), u'+')
        if (var.get(u'choice') == Js(8.0)):
            var.put(u'range', Js(130.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(9.0)):
            var.put(u'range', Js(100.0))
            var.put(u'width', Js(2.0))
            var.put(u'strthou', var.get(u'getRandomIndex')(Js(3.0)))
            var.put(u'strthou', var.get(u'fmt00000')(var.get(u'strthou'), Js(2.0)))
            var.put(u'str', var.get(u'strthou'), u'+')
            var.put(u'str', Js(u'-'), u'+')
            var.put(u'str', var.get(u'strthou'), u'+')
        if (var.get(u'choice') == Js(11.0)):
            var.put(u'range', Js(600.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(12.0)):
            var.put(u'range', Js(850.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(13.0)):
            var.put(u'range', Js(100.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(15.0)):
            var.put(u'range', Js(600.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(16.0)):
            var.put(u'range', Js(12000.0))
            var.put(u'width', Js(5.0))
        if (var.get(u'choice') == Js(17.0)):
            var.put(u'range', Js(30.0))
            var.put(u'width', Js(4.0))
            var.put(u'strmonth', var.get(u'getRandomIndex')(Js(13.0)))
            var.put(u'strmonth', var.get(u'fmt00000')(var.get(u'strmonth'), Js(2.0)))
            var.put(u'strdate', var.get(u'getRandomIndex')(Js(31.0)))
            var.put(u'strdate', var.get(u'fmt00000')(var.get(u'strdate'), Js(2.0)))
            var.put(u'str', var.get(u'strmonth'), u'+')
            var.put(u'str', var.get(u'strdate'), u'+')
        if (var.get(u'choice') == Js(18.0)):
            var.put(u'range', Js(50.0))
            var.put(u'width', Js(3.0))
            var.put(u'stryear', var.get(u'getRandomIndex')(Js(3.0)))
            var.put(u'stryear', var.get(u'fmt00000')(var.get(u'stryear'), Js(2.0)))
            var.put(u'strmonth', var.get(u'getRandomIndex')(Js(13.0)))
            if (var.get(u'strmonth') == Js(10.0)):
                var.put(u'strmonth', Js(u'a'))
            if (var.get(u'strmonth') == Js(11.0)):
                var.put(u'strmonth', Js(u'b'))
            if (var.get(u'strmonth') == Js(12.0)):
                var.put(u'strmonth', Js(u'c'))
            var.put(u'strdate', var.get(u'getRandomIndex')(Js(31.0)))
            var.put(u'strdate', var.get(u'fmt00000')(var.get(u'strdate'), Js(2.0)))
            var.put(u'str', var.get(u'stryear'), u'+')
            var.put(u'str', var.get(u'strmonth'), u'+')
            var.put(u'str', var.get(u'strdate'), u'+')
        if (var.get(u'choice') == Js(19.0)):
            var.put(u'range', Js(2000.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(20.0)):
            var.put(u'range', Js(200.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(22.0)):
            var.put(u'range', Js(3700.0))
            var.put(u'width', Js(4.0))
        if (var.get(u'choice') == Js(23.0)):
            var.put(u'range', Js(300.0))
            var.put(u'width', Js(4.0))
        var.put(u'strfoo', var.get(u'getRandomIndex')(var.get(u'range')))
        var.put(u'strfoo', var.get(u'fmt00000')(var.get(u'strfoo'), var.get(u'width')))
        var.put(u'str', var.get(u'strfoo'), u'+')
        if (var.get(u'choice') == Js(14.0)):
            var.put(u'strsize', var.get(u'getRandomIndex')(Js(3.0)))
            if (var.get(u'strsize') == Js(0.0)):
                var.put(u'strsize', Js(u's'))
            if (var.get(u'strsize') == Js(1.0)):
                var.put(u'strsize', Js(u'm'))
            if (var.get(u'strsize') == Js(2.0)):
                var.put(u'strsize', Js(u'l'))
            var.put(u'strnumber', var.get(u'getRandomIndex')(Js(190.0)))
            var.put(u'strnumber', var.get(u'fmt00000')(var.get(u'strnumber'), Js(4.0)))
            var.put(u'str', var.get(u'cams').get(var.get(u'choice')))
            var.put(u'str', var.get(u'strnumber'), u'+')
            var.put(u'str', var.get(u'strsize'), u'+')
        if (var.get(u'choice') == Js(21.0)):
            var.put(u'range', Js(100.0))
            var.put(u'width', Js(2.0))
            var.put(u'strthou', var.get(u'getRandomIndex')(Js(90.0)))
            var.put(u'strthou', var.get(u'fmt00000')(var.get(u'strthou'), Js(2.0)))
            var.put(u'str', Js(u'1'))
            var.put(u'str', var.get(u'strthou'), u'+')
            var.put(u'str', Js(u'-'), u'+')
            var.put(u'str', var.get(u'strthou'), u'+')
            var.put(u'strfoo', var.get(u'getRandomIndex')(var.get(u'range')))
            var.put(u'strfoo', var.get(u'fmt00000')(var.get(u'strfoo'), var.get(u'width')))
            var.put(u'str', var.get(u'strfoo'), u'+')
            var.put(u'str', Js(u'_IMG'), u'+')
        if (var.get(u'choice') == Js(25.0)):
            var.put(u'stryear', var.get(u'getRandomIndex')(Js(3.0)))
            var.put(u'stryear', (var.get(u'stryear') + Js(7.0)))
            var.put(u'stryear', var.get(u'fmt00000')(var.get(u'stryear'), Js(2.0)))
            var.put(u'strmonth', var.get(u'getRandomIndex')(Js(11.0)))
            var.put(u'strmonth', (var.get(u'strmonth') + Js(1.0)))
            var.put(u'strmonth', var.get(u'fmt00000')(var.get(u'strmonth'), Js(2.0)))
            var.put(u'strdate', var.get(u'getRandomIndex')(Js(30.0)))
            var.put(u'strdate', (var.get(u'strdate') + Js(1.0)))
            var.put(u'strdate', var.get(u'fmt00000')(var.get(u'strdate'), Js(2.0)))
            var.put(u'str', var.get(u'cams').get(var.get(u'choice')))
            var.put(u'str', Js(u'20'), u'+')
            var.put(u'str', var.get(u'stryear'), u'+')
            var.put(u'str', var.get(u'strmonth'), u'+')
            var.put(u'str', var.get(u'strdate'), u'+')
            var.put(u'str', Js(u'_*'), u'+')
        var.put(u'url', (var.get(u'str') + Js(u'.jpg')))
        return var.get(u'url')

    PyJsHoisted_generateFileName_.func_name = u'generateFileName'
    var.put(u'generateFileName', PyJsHoisted_generateFileName_)

    # modified
    return str(var.get(u'generateFileName')()).replace("'", '')


if __name__ == '__main__':
    print(get_random_search_term())
