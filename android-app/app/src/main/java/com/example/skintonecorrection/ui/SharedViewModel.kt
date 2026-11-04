package com.example.skintonecorrection.ui

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.skintonecorrection.data.ImageRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

enum class ProcessingState { IDLE, PROCESSING, SUCCESS, ERROR }
data class SharedUiState(
    val selectedImageUri:Uri?=null,val correctedImageUri:Uri?=null,val photoUsedUri:Uri?=null,
    val maskUri:Uri?=null,val reportUri:Uri?=null,val processingState:ProcessingState=ProcessingState.IDLE,
    val errorMessageRes:Int?=null,val message:String=""
)
class SharedViewModel(application:Application):AndroidViewModel(application) {
    private val repository=ImageRepository(application)
    private val mutable=MutableStateFlow(SharedUiState());val uiState=mutable.asStateFlow()
    private var job:Job?=null;private var generation=0
    fun selectImage(uri:Uri){job?.cancel();generation++;mutable.value=SharedUiState(selectedImageUri=uri)}
    fun startProcessing(){
        val uri=mutable.value.selectedImageUri ?: return
        if(mutable.value.processingState==ProcessingState.PROCESSING)return
        val token=++generation
        mutable.update{it.copy(processingState=ProcessingState.PROCESSING,correctedImageUri=null,reportUri=null,maskUri=null,photoUsedUri=null,message="Processing locally…")}
        job=viewModelScope.launch {
            try {
                val result=repository.runCorrection(uri)
                if(token==generation)mutable.update{it.copy(processingState=if(result.success)ProcessingState.SUCCESS else ProcessingState.ERROR,
                    correctedImageUri=result.corrected,photoUsedUri=result.input,maskUri=result.mask,reportUri=result.report,message=result.message)}
            }catch(cancelled:CancellationException){throw cancelled}
            catch(error:Exception){if(token==generation)mutable.update{it.copy(processingState=ProcessingState.ERROR,message="The app could not finish: "+(error.message ?: "unknown error"))}}
        }
    }
    fun export(source:Uri,destination:Uri,onFinished:(String)->Unit){viewModelScope.launch {
        try{repository.export(source,destination);onFinished("Saved to your chosen location.")}
        catch(cancelled:CancellationException){throw cancelled}
        catch(error:Exception){onFinished("Could not save. Choose another location.")}
    }}
}
