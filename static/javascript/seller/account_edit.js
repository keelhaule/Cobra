$().ready( function(){
  //assign bootstrap classes
  $('button').addClass('btn');
  $('#asset_tabs').addClass('nav').addClass('nav-tabs');
  $('#asset_tabs').children('li').first().addClass('active');
  $('.file-button').addClass('btn').html('<i class="icon-camera"></i>');
  $('#artisan_tab').trigger('click');//activate first tab
  $('#title').trigger('click');//get out of the way
  addAssetForms();
});

$('.asset-tab').click(function(){
  //make this tab active
  $('.asset-tab').removeClass('active');
  $(this).addClass('active');
  //hide all asset containers, then show the right one
  $('.asset-container').hide();
  asset_ilk = $(this).attr('id').replace('_tab','');
  $('#'+asset_ilk+'_container').show();
})

$('#title').on('click', function(){
  $('#seller_form').slideToggle();
});

$('input:file').change(function(){
  $(this).closest('.asset').find('.image-text').attr('value', $(this).val());
  $(this).closest('form').submit();
  addAssetForms();
})

function addAssetForms(){
  //use jquery appendTo function to move blank asset forms
  //to asset containers so there is always at least one fresh one.

  //for each asset container
  $('.asset-container').each(function(){
    num_forms = 0;
    num_empty_forms = 0;

    //for each asset form inside the containter
    $(this).children('.asset').each(function(){
      //count empty forms
      image_text_element = $(this).find('form > .hidden-fields > .image-text').first();
      if (image_text_element.val() == ''){
        num_empty_forms++;
      }else{
        num_forms++;
      }
    });

    //if there are no empty forms, add one
    if (num_empty_forms == 0){
      //grab an empty form from the hidden .asset_forms div
      new_asset_form = $('#asset_forms > .asset').first().clone(true);
      //if not product container, hide category element
      ilk = $(this).attr('id').replace('_container','');
      if ( ilk !== 'product'){
        new_asset_form.find('.asset-category').hide();
      }
      //give it a new unique id
      unique_id = ilk + '_image_' + (num_forms+1).toString();
      new_asset_form.find('.asset-image').attr('id', unique_id);
      //place it in the container
      new_asset_form.appendTo($(this));
    }
  });
}
