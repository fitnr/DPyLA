from urllib import urlencode, urlopen
import settings
import json

class DPLA():

    def __init__(self,api_key=None):
        self.BASE_URL = "http://api.dp.la/v2/"
        if api_key is not None:
            self.api_key = api_key
        elif settings.api_key is not None:
            self.api_key = settings.api_key
        else:
            raise ValueError('DPLA API requires an api key. Run DPLA.get_key() to request one')
        if len(self.api_key) is not 32:
            raise ValueError("The DPLA key is in the required format. PLease check it again")

    def itemSearch(self,query=None,**kwargs):
        """
        Builds and performs item search.
        :query - a simple search query. Concatenate spaces with '+'. Boolean operators allowed
        :searchFields -  Dictionary of field : "search value" pairs. Value is searched for only in the specified
          field. List of available fields is at http://dp.la/info/developers/codex/responses/field-reference/
        :returnFields - Fields that should be returned for each record. If blank, all fields are returned.
         :facets -
        """
        #get the params as a dictionary

        if query:
            kwargs['query'] = query

        self.request = Request(**kwargs)

        self.url = self._buildUrl('items', kwargs)
        print self.url
        self.responseRaw = urlopen(self.url).read()
        self.response = json.loads(self.responseRaw)
        self.results = Results(self.response)

    def _buildUrl(self, type, kwargs=None):
        url = self.BASE_URL + type + "?"
        for param in kwargs:
            if self.request.__dict__.get(param, None):
                url += self.request.__dict__[param]
        url += "api_key=" + self.api_key
        return url

class Request():
    def __init__(self, query=None, searchFields=None,returnFields=None,facets=None,sort=None,pagination=None):
        self.params = locals()
        # Clear out object attributes
        self._flushPreviousValues()
        if query:
            self.query =  self._singleValueFormatter('q',query)
        if searchFields:
            self.searchFields= self._searchFieldsFormatter(searchFields)
        if returnFields:
            self.returnFields = self._multiValueFormatter('fields',returnFields)
        if facets:
            self._facets_init(facets)
        if sort:
            self._sort_init(sort)


    def _facets_init(self, facets):
        if facets['fields']:
            self.facets = self._multiValueFormatter('facets',facets['fields'])
            if facets['limit']:
                self.facets_limit =  self._singleValueFormatter('facets_limit', facets['limit'])


    def _sort_init(self, sort):
        if sort['field']:
            self.sort = self._singleValueFormatter('sort_by', sort['field'])
        if sort['spatial']:
            self.spatialSort = self._singleValueFormatter('sort_by_pin', ','.join(sort['distance_from']))
            if sort['field'] != "sourceResource.spatial.coordinates":
                self.sort = self._singleValueFormatter('sort_by', "sourceResource.spatial.coordinates")
                print 'Forced sort to coordinates to work with sort by pin'

    def _singleValueFormatter(self, param_name, value):
            return urlencode({param_name: value}) + "&"

    def _searchFieldsFormatter(self, searchFields):
        sf = [urlencode({k:v}) for k,v in searchFields.items() if k in settings.searchable_fields]
        return '&'.join(sf) + "&"

    def _multiValueFormatter(self, param_name, values):
        return urlencode({param_name: ','.join(values)}) + "&"

    def _flushPreviousValues(self):
        for param in self.params:
            self.__dict__[param] = None


class Results():
    def __init__(self, response):
        self.count = response['count']
        self.limit = response['limit']


    def _fieldGetName(self, field):
        """
        Returns the Python friendly attribute name for a DPLA field
        """
        return field.replace('.','-')

    def _fieldSetValue(self,field, value):
        """
        Sets value for an attribute corresponding to DPLA field.
        Some DPLA fields contain periods.
        """
        self.__dict__['fields'][self._fieldGetName(field)] = value

    def _fieldGetValue(self, field):
         return self.__dict__['fields'][self._fieldGetName(field)]






