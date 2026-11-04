package com.example.skintonecorrection.ml

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class DevelopmentMathTest {
    private fun bytes(name:String)=javaClass.classLoader!!.getResourceAsStream(name)!!.use{it.readBytes()}
    private fun fixture()=JSONObject(bytes("pipeline_parity.json").toString(Charsets.UTF_8))
    private fun array(a:org.json.JSONArray)=DoubleArray(a.length()){a.getDouble(it)}
    @Test fun fiveFeatureBaselineMatchesSavedPythonVectors(){
        val manifest=JSONObject(bytes("development_pipeline/manifest.json").toString(Charsets.UTF_8))
        val names=manifest.getJSONArray("features").let{a->List(a.length()){a.getString(it)}}
        val tree=PortableTreeAsset.parse(bytes("development_pipeline/baseline5.json"),manifest.getJSONObject("assets_sha256").getString("baseline5.json"),names)
        val rows=fixture().getJSONArray("tree");assertEquals(20,rows.length())
        for(i in 0 until rows.length()){val r=rows.getJSONObject(i);assertArrayEquals(array(r.getJSONArray("expected")),tree.predict(array(r.getJSONArray("features"))),0.0)}
    }
    @Test fun mstKnotsMidpointsAndEndpointsMatchPython(){
        val lookup=JSONObject(bytes("development_pipeline/mst_lookup.json").toString(Charsets.UTF_8))
        val x=array(lookup.getJSONArray("ita_knots"));val y=array(lookup.getJSONArray("mst_knots"))
        val rows=fixture().getJSONArray("mapping");assertEquals(47,rows.length())
        for(i in 0 until rows.length()){val r=rows.getJSONObject(i);assertEquals(r.getInt("expected"),DevelopmentMath.mst(r.getDouble("ita"),x,y))}
        assertEquals(9,DevelopmentMath.mst(-90.0,x,y));assertEquals(1,DevelopmentMath.mst(90.0,x,y))
    }
    @Test fun reciprocalCorrectionMatchesPythonAndPreservesAlpha(){
        val rows=fixture().getJSONArray("pixels");assertEquals(111,rows.length())
        for(i in 0 until rows.length()){val r=rows.getJSONObject(i);assertEquals(r.getInt("expected"),DevelopmentMath.correct(r.getInt("input"),array(r.getJSONArray("parameters"))))}
        val pixel=0x7f123456
        assertEquals(pixel,DevelopmentMath.correct(pixel,doubleArrayOf(1.0,1.0,1.0)))
    }
    @Test fun undefinedItaAndInvalidParametersFail(){
        try {DevelopmentMath.ita(50.0,0.0);fail()}catch(expected:IllegalArgumentException){}
        try {DevelopmentMath.correct(0,doubleArrayOf(0.0,1.0,1.0));fail()}catch(expected:IllegalArgumentException){}
        assertEquals(0.0,DevelopmentMath.ita(50.0,10.0),0.0)
    }
}
